# frozen_string_literal: true

require "test_helper"

module SwarmSDK
  module Tools
    module DocumentConverters
      class DocxConverterTest < Minitest::Test
        def setup
          @converter = DocxConverter.new
        end

        def test_converter_metadata
          assert_equal("docx", DocxConverter.gem_name)
          assert_equal("DOCX", DocxConverter.format_name)
          assert_equal([".docx", ".doc"], DocxConverter.extensions)
        end

        def test_convert_returns_error_when_gem_not_available
          # Stub available? to return false
          DocxConverter.stub(:available?, false) do
            result = @converter.convert("/tmp/test.docx")

            assert_instance_of(String, result)
            # The actual message is a system-reminder about installing the gem
            assert_includes(result, "required gem is not installed")
            assert_includes(result, "docx")
          end
        end

        def test_convert_rejects_legacy_doc_format
          skip("Requires docx gem") unless DocxConverter.available?

          Dir.mktmpdir do |dir|
            doc_file = File.join(dir, "test.doc")
            File.write(doc_file, "fake content")

            result = @converter.convert(doc_file)

            assert_instance_of(String, result)
            assert_includes(result, "DOC format is not supported")
            assert_includes(result, "convert to DOCX first")
          end
        end

        def test_convert_handles_zip_error
          skip("Requires docx gem") unless DocxConverter.available?

          # Create an invalid DOCX (not a zip file)
          Dir.mktmpdir do |dir|
            invalid_docx = File.join(dir, "invalid.docx")
            File.write(invalid_docx, "Not a zip file")

            result = @converter.convert(invalid_docx)

            assert_instance_of(String, result)
            assert_includes(result, "Invalid or corrupted DOCX file")
          end
        end

        def test_convert_handles_missing_file
          skip("Requires docx gem") unless DocxConverter.available?

          result = @converter.convert("/nonexistent/file.docx")

          assert_instance_of(String, result)
          # Error message format
          assert_match(/Error:/, result)
        end
      end
    end
  end
end
