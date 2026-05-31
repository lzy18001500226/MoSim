// protoc-gen-amesh-convert is a protoc plugin that generates Go domain↔proto
// converter functions from .proto annotations.
//
// Activation:
//   - .proto file imports "codegen/v1/options.proto" and adds
//     `option (amesh.codegen.v1.go_domain) = { type: "..." }` to messages.
//   - buf.amesh.gen.yaml (or `protoc --amesh-convert_out`) invokes this binary.
//   - Output: <message>_convert.amesh.go in the same Go package as the
//     proto bindings (paths=source_relative, so file lands next to
//     <message>.pb.go).
//
// Scope (Phase 12 M3):
//   - Mirror fields (proto field name → Go field via protoc-gen-go conv)
//   - field_rename annotation for non-mirror cases (org_id → OrganizationID)
//   - field_convert annotation for type bridging (rfc3339, rfc3339_ptr,
//     string_ptr, string_slice_cast)
//   - field_skip / field_custom / field_enum_map deferred to M4.
//
// Anti-scope:
//   - No domain struct verification via go/packages (M3 trusts annotation
//     + protoc-gen-go convention). go/packages introspection deferred to M4
//     because it requires resolving Go module paths inside protoc plugins.
//
// See plan: .claude/plans/goofy-doodling-zebra.md Phase 12 M3.

package main

import (
	"fmt"
	"strings"

	"google.golang.org/protobuf/compiler/protogen"
	"google.golang.org/protobuf/reflect/protoreflect"
	"google.golang.org/protobuf/types/pluginpb"
)

// protoconv helper package — emit calls to functions defined here for
// time / nullable / slice conversions. Path is fully qualified so
// `g.QualifiedGoIdent` injects the import automatically.
const protoconvImportPath = "github.com/anthropics/agentsmesh/backend/pkg/protoconv"

// flatOutput, when set via the protoc plugin option `flat=1`, causes the
// plugin to emit `<base>_convert.amesh.go` directly under protoc's `out`
// directory instead of nested under `convert_target.output_dir`.
//
// Used by the Bazel macro (`amesh_proto_convert`) — Bazel declares the
// output file path at rule-evaluation time, so the plugin needs to write
// a known basename, not an annotation-derived sub-path.
//
// The buf workflow leaves this unset; plugin writes to
// `<output_dir>/<base>_convert.amesh.go` relative to buf's `out: .`.
var flatOutput bool

func main() {
	opts := protogen.Options{
		ParamFunc: func(name, value string) error {
			switch name {
			case "flat":
				flatOutput = value == "1" || value == "true"
			}
			return nil
		},
	}
	opts.Run(func(plugin *protogen.Plugin) error {
		plugin.SupportedFeatures = uint64(pluginpb.CodeGeneratorResponse_FEATURE_PROTO3_OPTIONAL)
		return generate(plugin)
	})
}

func generate(plugin *protogen.Plugin) error {
	for _, file := range plugin.Files {
		if !file.Generate {
			continue
		}
		if err := generateFile(plugin, file); err != nil {
			return err
		}
	}
	return nil
}

func generateFile(plugin *protogen.Plugin, file *protogen.File) error {
	messages := collectAnnotatedMessages(file)
	if len(messages) == 0 {
		return nil
	}

	target, ok := readFileTarget(file)
	if !ok {
		return fmt.Errorf("%s: messages are annotated with (amesh.codegen.v1.go_domain) but the file is missing the (amesh.codegen.v1.convert_target) option — codegen cannot place the output without an explicit output_dir/output_package", file.Desc.Path())
	}

	base := protoBasename(file)
	var filename string
	if flatOutput {
		// Bazel-driven invocation — emit directly under protoc's `out`
		// dir (declared at rule-evaluation time by amesh_proto_convert).
		filename = base + "_convert.amesh.go"
	} else {
		// buf-driven invocation — nest under the annotation's output_dir
		// so the file lands in the backend handler tree relative to
		// buf's `out: .` (workspace root).
		filename = target.OutputDir + "/" + base + "_convert.amesh.go"
	}

	// The Go package of the generated file is the handler package, not
	// the proto package.
	handlerImportPath := protogen.GoImportPath(workspaceImportPath(target.OutputDir))
	g := plugin.NewGeneratedFile(filename, handlerImportPath)

	writeHeader(g, file, target.OutputPackage)

	// Proto types live in their own Go package; reference them via the
	// proto file's GoImportPath so the handler-side codegen emits the
	// `bindingv1` qualifier on Pod/PodBinding/etc.
	for _, m := range messages {
		if err := writeMessageConvert(g, m, file.GoImportPath); err != nil {
			return fmt.Errorf("message %s: %w", m.proto.Desc.Name(), err)
		}
	}
	return nil
}

// protoBasename extracts the base filename without directory or extension.
// e.g. "binding/v1/binding.proto" → "binding".
func protoBasename(file *protogen.File) string {
	path := file.Desc.Path()
	if i := strings.LastIndex(path, "/"); i >= 0 {
		path = path[i+1:]
	}
	if i := strings.LastIndex(path, "."); i >= 0 {
		path = path[:i]
	}
	return path
}

// workspaceImportPath maps a workspace-relative dir to a Go import path.
// `backend/internal/api/connect/binding` → `github.com/anthropics/agentsmesh/backend/internal/api/connect/binding`.
const goModulePrefix = "github.com/anthropics/agentsmesh/"

func workspaceImportPath(dir string) string {
	return goModulePrefix + strings.TrimPrefix(dir, "/")
}

func writeHeader(g *protogen.GeneratedFile, file *protogen.File, pkg string) {
	g.P("// Code generated by protoc-gen-amesh-convert. DO NOT EDIT.")
	g.P("// source: ", file.Desc.Path())
	g.P()
	g.P("package ", pkg)
	g.P()
}

func writeMessageConvert(g *protogen.GeneratedFile, m *annotatedMessage, protoImportPath protogen.GoImportPath) error {
	importPath, typeName, err := splitGoQualifiedType(m.annotation.Type)
	if err != nil {
		return err
	}

	domainIdent := g.QualifiedGoIdent(protogen.GoIdent{
		GoName:       typeName,
		GoImportPath: protogen.GoImportPath(importPath),
	})

	// Proto Go ident — reference through the proto package, qualifying with
	// the proto Go import path so the generated handler-side file emits
	// `bindingv1.PodBinding` (not just `PodBinding` like the in-package codegen).
	protoIdent := g.QualifiedGoIdent(protogen.GoIdent{
		GoName:       m.proto.GoIdent.GoName,
		GoImportPath: protoImportPath,
	})
	// Function names use the local type name (PodBinding), not the qualified form.
	protoTypeName := m.proto.GoIdent.GoName

	if m.annotation.GenerateToProto {
		g.P("// ToProto", protoTypeName, " converts the domain type to its proto wire shape.")
		g.P("func ToProto", protoTypeName, "(d *", domainIdent, ") *", protoIdent, " {")
		g.P("\tif d == nil { return nil }")
		g.P("\treturn &", protoIdent, "{")
		for _, f := range m.fields {
			line, err := generateToProtoField(g, m.proto.Desc.Name(), f)
			if err != nil {
				return err
			}
			if line != "" {
				g.P("\t\t", line, ",")
			}
		}
		g.P("\t}")
		g.P("}")
		g.P()
	}

	if m.annotation.GenerateFromProto {
		g.P("// FromProto", protoTypeName, " converts the proto wire shape to its domain type.")
		g.P("func FromProto", protoTypeName, "(p *", protoIdent, ") *", domainIdent, " {")
		g.P("\tif p == nil { return nil }")
		g.P("\treturn &", domainIdent, "{")
		for _, f := range m.fields {
			line, err := generateFromProtoField(g, m.proto.Desc.Name(), f)
			if err != nil {
				return err
			}
			if line != "" {
				g.P("\t\t", line, ",")
			}
		}
		g.P("\t}")
		g.P("}")
		g.P()
	}
	return nil
}

// generateToProtoField emits one struct-init line for the proto side.
// Mirror: `ProtoField: d.DomainField`. Converted: `ProtoField: protoconv.X(d.DomainField)`.
// custom:   `ProtoField: customFn(d.DomainField)` — user-provided helper in
//
//	`<file>_convert_custom.go` (same package).
//
// Returns an error if convertKind is set but unknown — caller writes
// it back as a protoc plugin error so buf/Bazel surface it clearly with
// the proto file + message context.
func generateToProtoField(g *protogen.GeneratedFile, msgName protoreflect.Name, f *fieldMapping) (string, error) {
	if f.skip {
		return "", nil
	}
	rhs := fmt.Sprintf("d.%s", f.domainFieldName)
	switch {
	case f.customFn != "":
		rhs = fmt.Sprintf("%s(%s)", f.customFn, rhs)
	case f.convertKind != "":
		helper := protoconvHelper(g, f.convertKind, true)
		if helper == "" {
			return "", fmt.Errorf("%s.%s: unknown field_convert %q (supported: rfc3339, rfc3339_ptr, rfc3339_nano, rfc3339_nano_ptr, string_ptr, string_slice_cast, int_to_int32, int_to_int64, int_ptr_to_int32, int_ptr_to_int64)", msgName, f.protoFieldName, f.convertKind)
		}
		rhs = fmt.Sprintf("%s(%s)", helper, rhs)
	}
	return fmt.Sprintf("%s: %s", f.protoFieldName, rhs), nil
}

// generateFromProtoField emits the inverse struct-init line.
func generateFromProtoField(g *protogen.GeneratedFile, msgName protoreflect.Name, f *fieldMapping) (string, error) {
	if f.skip {
		return "", nil
	}
	rhs := fmt.Sprintf("p.%s", f.protoFieldName)
	switch {
	case f.customFn != "":
		// Custom function name convention: ToProto half is `fooToProto`,
		// FromProto half is `fooFromProto`. If the user supplied just one
		// name we assume the suffix flips. (M4 keeps this simple — most
		// callers either set both directions or skip the reverse via
		// generate_from_proto: false on the message option.)
		rhs = fmt.Sprintf("%s(%s)", reverseCustomFnName(f.customFn), rhs)
	case f.convertKind != "":
		helper := protoconvHelper(g, f.convertKind, false)
		if helper == "" {
			return "", fmt.Errorf("%s.%s: unknown field_convert %q", msgName, f.protoFieldName, f.convertKind)
		}
		rhs = fmt.Sprintf("%s(%s)", helper, rhs)
	}
	return fmt.Sprintf("%s: %s", f.domainFieldName, rhs), nil
}

// reverseCustomFnName flips the "ToProto" suffix in a custom function name to
// "FromProto" (and vice versa). Returns the original name if no suffix matches.
//
// Examples:
//
//	"specToProto"     → "specFromProto"
//	"statusFromProto" → "statusToProto"
//	"customMapper"    → "customMapper"   (unchanged; caller must supply both)
func reverseCustomFnName(name string) string {
	const toSuffix = "ToProto"
	const fromSuffix = "FromProto"
	if strings.HasSuffix(name, toSuffix) {
		return name[:len(name)-len(toSuffix)] + fromSuffix
	}
	if strings.HasSuffix(name, fromSuffix) {
		return name[:len(name)-len(fromSuffix)] + toSuffix
	}
	return name
}

// protoconvHelper resolves a field_convert tag to the fully-qualified
// helper-function identifier. Returns empty string when the tag is unknown
// (codegen falls back to mirror — M4 turns this into a hard error).
//
// `toProto` selects forward vs reverse direction. Some conversions are
// symmetric (StringPtr); others have direction-specific names
// (RFC3339 / ParseRFC3339).
func protoconvHelper(g *protogen.GeneratedFile, kind string, toProto bool) string {
	name := protoconvFuncName(kind, toProto)
	if name == "" {
		return ""
	}
	return g.QualifiedGoIdent(protogen.GoIdent{
		GoName:       name,
		GoImportPath: protogen.GoImportPath(protoconvImportPath),
	})
}

func protoconvFuncName(kind string, toProto bool) string {
	if toProto {
		switch kind {
		case "rfc3339":
			return "RFC3339"
		case "rfc3339_ptr":
			return "RFC3339Ptr"
		case "rfc3339_nano":
			return "RFC3339Nano"
		case "rfc3339_nano_ptr":
			return "RFC3339NanoPtr"
		case "string_ptr":
			return "StringPtr"
		case "string_slice_cast":
			return "StringSlice"
		case "int_to_int32":
			return "IntToInt32"
		case "int_to_int64":
			return "IntToInt64"
		case "int_ptr_to_int32":
			return "IntPtrToInt32Ptr"
		case "int_ptr_to_int64":
			return "IntPtrToInt64Ptr"
		}
	} else {
		switch kind {
		case "rfc3339":
			return "ParseRFC3339"
		case "rfc3339_ptr":
			return "ParseRFC3339Ptr"
		case "rfc3339_nano":
			return "ParseRFC3339Nano"
		case "rfc3339_nano_ptr":
			return "ParseRFC3339NanoPtr"
		case "string_ptr":
			return "StringPtr"
		case "string_slice_cast":
			return "StringArray"
		case "int_to_int32":
			return "Int32ToInt"
		case "int_to_int64":
			return "Int64ToInt"
		case "int_ptr_to_int32":
			return "Int32PtrToIntPtr"
		case "int_ptr_to_int64":
			return "Int64PtrToIntPtr"
		}
	}
	return ""
}

func splitGoQualifiedType(qualified string) (importPath, typeName string, err error) {
	idx := strings.LastIndex(qualified, ".")
	if idx < 0 {
		return "", "", fmt.Errorf("go_domain.type must be fully qualified (got %q)", qualified)
	}
	return qualified[:idx], qualified[idx+1:], nil
}
