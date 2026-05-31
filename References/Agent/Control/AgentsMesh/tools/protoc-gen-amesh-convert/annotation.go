// annotation discovery + field mapping.
//
// Reads `(amesh.codegen.v1.go_domain)` message option + per-field options
// via the typed extension API (`proto.GetExtension`). The codegen package
// from `proto/gen/go/codegen/v1` provides the strongly-typed
// `E_GoDomain` / `E_FieldRename` etc. extension descriptors that protoc-gen-go
// emits for `extend google.protobuf.MessageOptions { ... }` declarations.
//
// We MUST go through the typed API — `protoreflect.Range` only surfaces
// extensions that are registered on the descriptor pool of the plugin
// process. By importing codegenv1 we register the extension descriptors
// at init time, but typed access via GetExtension is the official path.

package main

import (
	"strings"

	codegenv1 "github.com/anthropics/agentsmesh/proto/gen/go/codegen/v1"
	"google.golang.org/protobuf/compiler/protogen"
	"google.golang.org/protobuf/proto"
	"google.golang.org/protobuf/types/descriptorpb"
)

type annotatedMessage struct {
	proto      *protogen.Message
	annotation goDomainAnnotation
	fields     []*fieldMapping
}

type goDomainAnnotation struct {
	Type              string
	GenerateToProto   bool
	GenerateFromProto bool
}

// fileTarget mirrors amesh.codegen.v1.ConvertTarget — declares where the
// convert codegen output file lands. Required because proto packages
// cannot import backend internal/ packages, so the convert function must
// live inside the backend connect handler tree.
type fileTarget struct {
	OutputDir     string
	OutputPackage string
}

func readFileTarget(file *protogen.File) (fileTarget, bool) {
	opts, ok := file.Desc.Options().(*descriptorpb.FileOptions)
	if !ok || opts == nil {
		return fileTarget{}, false
	}
	if !proto.HasExtension(opts, codegenv1.E_ConvertTarget) {
		return fileTarget{}, false
	}
	ext, _ := proto.GetExtension(opts, codegenv1.E_ConvertTarget).(*codegenv1.ConvertTarget)
	if ext == nil || ext.GetOutputDir() == "" || ext.GetOutputPackage() == "" {
		return fileTarget{}, false
	}
	return fileTarget{
		OutputDir:     strings.TrimSpace(ext.GetOutputDir()),
		OutputPackage: strings.TrimSpace(ext.GetOutputPackage()),
	}, true
}

type fieldMapping struct {
	protoFieldName  string
	domainFieldName string
	skip            bool
	customFn        string
	enumFn          string
	// convertKind == "" means mirror passthrough (assign as-is).
	// Other values trigger protoconv helper calls (rfc3339, rfc3339_ptr,
	// string_ptr, string_slice_cast, ...) — see options.proto FieldConvert.
	convertKind string
}

func collectAnnotatedMessages(file *protogen.File) []*annotatedMessage {
	var out []*annotatedMessage
	for _, m := range file.Messages {
		ann, ok := readGoDomainAnnotation(m)
		if !ok {
			continue
		}
		// Default both directions on if neither is set — most messages
		// want round-trip codegen.
		if !ann.GenerateToProto && !ann.GenerateFromProto {
			ann.GenerateToProto = true
			ann.GenerateFromProto = true
		}
		out = append(out, &annotatedMessage{
			proto:      m,
			annotation: ann,
			fields:     collectFieldMappings(m),
		})
	}
	return out
}

func readGoDomainAnnotation(m *protogen.Message) (goDomainAnnotation, bool) {
	opts, ok := m.Desc.Options().(*descriptorpb.MessageOptions)
	if !ok || opts == nil {
		return goDomainAnnotation{}, false
	}
	if !proto.HasExtension(opts, codegenv1.E_GoDomain) {
		return goDomainAnnotation{}, false
	}
	ext, _ := proto.GetExtension(opts, codegenv1.E_GoDomain).(*codegenv1.GoDomain)
	if ext == nil || ext.GetType() == "" {
		return goDomainAnnotation{}, false
	}
	return goDomainAnnotation{
		Type:              strings.TrimSpace(ext.GetType()),
		GenerateToProto:   ext.GetGenerateToProto(),
		GenerateFromProto: ext.GetGenerateFromProto(),
	}, true
}

func collectFieldMappings(m *protogen.Message) []*fieldMapping {
	out := make([]*fieldMapping, 0, len(m.Fields))
	for _, f := range m.Fields {
		fm := &fieldMapping{
			protoFieldName:  f.GoName,
			domainFieldName: f.GoName,
		}
		readFieldOptions(f, fm)
		out = append(out, fm)
	}
	return out
}

func readFieldOptions(f *protogen.Field, fm *fieldMapping) {
	opts, ok := f.Desc.Options().(*descriptorpb.FieldOptions)
	if !ok || opts == nil {
		return
	}
	if proto.HasExtension(opts, codegenv1.E_FieldRename) {
		if v, ok := proto.GetExtension(opts, codegenv1.E_FieldRename).(string); ok {
			if s := strings.TrimSpace(v); s != "" {
				fm.domainFieldName = s
			}
		}
	}
	if proto.HasExtension(opts, codegenv1.E_FieldEnumMap) {
		if v, ok := proto.GetExtension(opts, codegenv1.E_FieldEnumMap).(string); ok {
			fm.enumFn = strings.TrimSpace(v)
		}
	}
	if proto.HasExtension(opts, codegenv1.E_FieldSkip) {
		if v, ok := proto.GetExtension(opts, codegenv1.E_FieldSkip).(bool); ok {
			fm.skip = v
		}
	}
	if proto.HasExtension(opts, codegenv1.E_FieldCustom) {
		if v, ok := proto.GetExtension(opts, codegenv1.E_FieldCustom).(string); ok {
			fm.customFn = strings.TrimSpace(v)
		}
	}
	if proto.HasExtension(opts, codegenv1.E_FieldConvert) {
		if v, ok := proto.GetExtension(opts, codegenv1.E_FieldConvert).(string); ok {
			fm.convertKind = strings.TrimSpace(v)
		}
	}
}
