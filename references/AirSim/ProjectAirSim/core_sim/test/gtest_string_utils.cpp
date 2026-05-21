// Copyright (C) Microsoft Corporation. 
// Copyright (C) 2025 IAMAI CONSULTING CORP

// MIT License. All rights reserved.

#include "gtest/gtest.h"
#include "string_utils.hpp"

namespace projectairsim = microsoft::projectairsim;

TEST(StringUtils, LTrim) {
  // General description:
  // Verifies ltrim for StringUtils.
  // Arrange: prepare context for `std::string string("abc");`.
  std::string string("abc");
  // Act: run `projectairsim::StringUtils::LTrim(string);`.
  projectairsim::StringUtils::LTrim(string);
  // Assert: check result from `EXPECT_EQ(string, "abc");`.
  EXPECT_EQ(string, "abc");

  string = " abc";
  projectairsim::StringUtils::LTrim(string);
  EXPECT_EQ(string, "abc");

  string = "   abc";
  projectairsim::StringUtils::LTrim(string);
  EXPECT_EQ(string, "abc");

  string = "abc ";
  projectairsim::StringUtils::LTrim(string);
  EXPECT_EQ(string, "abc ");

  string = " abc ";
  projectairsim::StringUtils::LTrim(string);
  EXPECT_EQ(string, "abc ");
}

TEST(StringUtils, RTrim) {
  // General description:
  // Verifies rtrim for StringUtils.
  // Arrange: prepare context for `std::string string("abc");`.
  std::string string("abc");
  // Act: run `projectairsim::StringUtils::RTrim(string);`.
  projectairsim::StringUtils::RTrim(string);
  // Assert: check result from `EXPECT_EQ(string, "abc");`.
  EXPECT_EQ(string, "abc");

  string = "abc ";
  projectairsim::StringUtils::RTrim(string);
  EXPECT_EQ(string, "abc");

  string = "abc   ";
  projectairsim::StringUtils::RTrim(string);
  EXPECT_EQ(string, "abc");

  string = " abc";
  projectairsim::StringUtils::RTrim(string);
  EXPECT_EQ(string, " abc");

  string = " abc ";
  projectairsim::StringUtils::RTrim(string);
  EXPECT_EQ(string, " abc");
}

TEST(StringUtils, Trim) {
  // General description:
  // Verifies trim for StringUtils.
  // Arrange: prepare context for `std::string string("abc");`.
  std::string string("abc");
  // Act: run `projectairsim::StringUtils::Trim(string);`.
  projectairsim::StringUtils::Trim(string);
  // Assert: check result from `EXPECT_EQ(string, "abc");`.
  EXPECT_EQ(string, "abc");

  string = "abc ";
  projectairsim::StringUtils::Trim(string);
  EXPECT_EQ(string, "abc");

  string = "abc   ";
  projectairsim::StringUtils::Trim(string);
  EXPECT_EQ(string, "abc");

  string = " abc";
  projectairsim::StringUtils::Trim(string);
  EXPECT_EQ(string, "abc");

  string = "   abc";
  projectairsim::StringUtils::Trim(string);
  EXPECT_EQ(string, "abc");

  string = " abc ";
  projectairsim::StringUtils::Trim(string);
  EXPECT_EQ(string, "abc");

  string = "   abc   ";
  projectairsim::StringUtils::Trim(string);
  EXPECT_EQ(string, "abc");
}

TEST(StringUtils, LTrimCopy) {
  // General description:
  // Verifies ltrim copy for StringUtils.
  // Arrange: prepare context for `EXPECT_EQ(projectairsim::StringUtils::LTrimCopy("abc"), "abc");`.
  // Act: run `EXPECT_EQ(projectairsim::StringUtils::LTrimCopy("abc"), "abc");`.
  // Assert: check result from `EXPECT_EQ(projectairsim::StringUtils::LTrimCopy("abc"), "abc");`.
  EXPECT_EQ(projectairsim::StringUtils::LTrimCopy("abc"), "abc");
  EXPECT_EQ(projectairsim::StringUtils::LTrimCopy(" abc"), "abc");
  EXPECT_EQ(projectairsim::StringUtils::LTrimCopy("   abc"), "abc");
  EXPECT_EQ(projectairsim::StringUtils::LTrimCopy("abc "), "abc ");
  EXPECT_EQ(projectairsim::StringUtils::LTrimCopy(" abc "), "abc ");
}

TEST(StringUtils, RTrimCopy) {
  // General description:
  // Verifies rtrim copy for StringUtils.
  // Arrange: prepare context for `EXPECT_EQ(projectairsim::StringUtils::RTrimCopy("abc"), "abc");`.
  // Act: run `EXPECT_EQ(projectairsim::StringUtils::RTrimCopy("abc"), "abc");`.
  // Assert: check result from `EXPECT_EQ(projectairsim::StringUtils::RTrimCopy("abc"), "abc");`.
  EXPECT_EQ(projectairsim::StringUtils::RTrimCopy("abc"), "abc");
  EXPECT_EQ(projectairsim::StringUtils::RTrimCopy("abc "), "abc");
  EXPECT_EQ(projectairsim::StringUtils::RTrimCopy("abc   "), "abc");
  EXPECT_EQ(projectairsim::StringUtils::RTrimCopy(" abc"), " abc");
  EXPECT_EQ(projectairsim::StringUtils::RTrimCopy(" abc "), " abc");
}

TEST(StringUtils, TrimCopy) {
  // General description:
  // Verifies trim copy for StringUtils.
  // Arrange: prepare context for `EXPECT_EQ(projectairsim::StringUtils::TrimCopy("abc"), "abc");`.
  // Act: run `EXPECT_EQ(projectairsim::StringUtils::TrimCopy("abc"), "abc");`.
  // Assert: check result from `EXPECT_EQ(projectairsim::StringUtils::TrimCopy("abc"), "abc");`.
  EXPECT_EQ(projectairsim::StringUtils::TrimCopy("abc"), "abc");
  EXPECT_EQ(projectairsim::StringUtils::TrimCopy("abc "), "abc");
  EXPECT_EQ(projectairsim::StringUtils::TrimCopy("abc   "), "abc");
  EXPECT_EQ(projectairsim::StringUtils::TrimCopy(" abc"), "abc");
  EXPECT_EQ(projectairsim::StringUtils::TrimCopy("   abc"), "abc");
  EXPECT_EQ(projectairsim::StringUtils::TrimCopy(" abc "), "abc");
  EXPECT_EQ(projectairsim::StringUtils::TrimCopy("   abc   "), "abc");
}
