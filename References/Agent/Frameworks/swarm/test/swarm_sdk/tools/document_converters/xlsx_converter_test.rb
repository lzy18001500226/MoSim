# frozen_string_literal: true

require "test_helper"

module SwarmSDK
  module Tools
    module DocumentConverters
      class XlsxConverterTest < Minitest::Test
        def setup
          @converter = XlsxConverter.new
        end

        def test_converter_metadata
          assert_equal("roo", XlsxConverter.gem_name)
          assert_equal("XLSX/XLS", XlsxConverter.format_name)
          assert_equal([".xlsx", ".xls"], XlsxConverter.extensions)
        end

        def test_xls_gem_available_check
          # Test the class method exists
          assert_respond_to(XlsxConverter, :xls_gem_available?)
        end

        def test_convert_returns_error_when_roo_not_available
          XlsxConverter.stub(:available?, false) do
            result = @converter.convert("/tmp/test.xlsx")

            assert_instance_of(String, result)
            assert_includes(result, "required gem is not installed")
            assert_includes(result, "roo")
          end
        end

        def test_convert_rejects_xls_without_roo_xls_gem
          skip("Requires roo gem") unless XlsxConverter.available?

          # Stub xls_gem_available? to return false
          XlsxConverter.stub(:xls_gem_available?, false) do
            Dir.mktmpdir do |dir|
              xls_file = File.join(dir, "test.xls")
              File.write(xls_file, "fake content")

              result = @converter.convert(xls_file)

              assert_instance_of(String, result)
              assert_includes(result, "Legacy .xls files require")
              assert_includes(result, "roo-xls")
            end
          end
        end

        def test_convert_handles_argument_error
          skip("Requires roo gem") unless XlsxConverter.available?

          Dir.mktmpdir do |dir|
            invalid_file = File.join(dir, "invalid.xlsx")
            File.write(invalid_file, "not a spreadsheet")

            result = @converter.convert(invalid_file)

            assert_instance_of(String, result)
            assert_match(/Error:.*Failed to open spreadsheet|Corrupted/, result)
          end
        end

        def test_convert_handles_zip_error
          skip("Requires roo gem") unless XlsxConverter.available?

          Dir.mktmpdir do |dir|
            invalid_file = File.join(dir, "invalid.xlsx")
            File.write(invalid_file, "not a zip file")

            result = @converter.convert(invalid_file)

            assert_instance_of(String, result)
            assert_match(/Error:/, result)
          end
        end

        def test_convert_handles_io_error
          skip("Requires roo gem") unless XlsxConverter.available?

          # Non-existent file triggers IO error
          result = @converter.convert("/nonexistent/file.xlsx")

          assert_instance_of(String, result)
          assert_match(/Error:/, result)
        end

        def test_convert_handles_general_error
          skip("Requires roo gem") unless XlsxConverter.available?

          # This tests the StandardError rescue
          result = @converter.convert("/invalid/path.xlsx")

          assert_instance_of(String, result)
          assert_match(/Error:/, result)
        end

        # Cell type formatting tests - these test the format_cell_value case statement
        # Note: Can't easily test without real spreadsheet, but branches exist:
        # - :string, :float, :number, :date, :datetime, :time
        # - :boolean, :formula, :link, :percentage, else
        # These would require creating actual XLSX files with different cell types
      end
    end
  end
end
