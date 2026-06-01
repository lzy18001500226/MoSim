# frozen_string_literal: true

require "test_helper"

module SwarmSDK
  module Tools
    module DocumentConverters
      class PdfConverterTest < Minitest::Test
        def setup
          @converter = PdfConverter.new
        end

        def test_converter_metadata
          assert_equal("pdf-reader", PdfConverter.gem_name)
          assert_equal("PDF", PdfConverter.format_name)
          assert_equal([".pdf"], PdfConverter.extensions)
        end

        def test_convert_returns_error_when_gem_not_available
          # Stub available? to return false
          PdfConverter.stub(:available?, false) do
            result = @converter.convert("/tmp/test.pdf")

            assert_instance_of(String, result)
            # The actual message is a system-reminder about installing the gem
            assert_includes(result, "required gem is not installed")
            assert_includes(result, "pdf-reader")
          end
        end

        def test_convert_handles_malformed_pdf_error
          skip("Requires pdf-reader gem") unless PdfConverter.available?

          # Create a file that will trigger MalformedPDFError
          Dir.mktmpdir do |dir|
            invalid_pdf = File.join(dir, "invalid.pdf")
            File.write(invalid_pdf, "Not a real PDF")

            result = @converter.convert(invalid_pdf)

            assert_instance_of(String, result)
            assert_includes(result, "PDF file is malformed")
          end
        end

        def test_convert_handles_unsupported_feature_error
          # This is difficult to test without a specific PDF
          # The branch is exercised when PDF::Reader::UnsupportedFeatureError is raised
          skip("Requires specific PDF with unsupported features")
        end

        def test_convert_handles_general_errors
          skip("Requires pdf-reader gem") unless PdfConverter.available?

          # Non-existent file will trigger StandardError path
          result = @converter.convert("/nonexistent/file.pdf")

          assert_instance_of(String, result)
          # Error message format
          assert_match(/Error:/, result)
        end
      end
    end
  end
end
