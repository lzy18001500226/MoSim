// Copyright (C) Microsoft Corporation. 
// Copyright (C) 2025 IAMAI CONSULTING CORP

// MIT License. All rights reserved.

#include <functional>
#include <iostream>
#include <string>

#include "core_sim/logger.hpp"
#include "gtest/gtest.h"

namespace projectairsim = microsoft::projectairsim;

void TestLog(projectairsim::LogLevel test_level,
             std::function<void(projectairsim::Logger&, std::string, const char*)>
                 log_func);

void TestLog(
    projectairsim::LogLevel test_level,
    std::function<void(projectairsim::Logger&, std::string, const char*, int)>
        log_func);

TEST(Logger, Constructor) {
                     // Act: run `auto callback = [](const std::string& component, projectairsim::LogLevel level,`.
  // General description:
  // Verifies constructor for Logger.
  // Arrange: prepare context for `auto callback = [](const std::string& component, projectairsim::LogLevel level,`.
  auto callback = [](const std::string& component, projectairsim::LogLevel level,
                     const std::string& message) {};

  // Assert: check result from `EXPECT_NE(std::make_unique<projectairsim::Logger>(`.
  EXPECT_NE(std::make_unique<projectairsim::Logger>(
                callback, projectairsim::LogLevel::kVerbose),
            nullptr);

  EXPECT_NE(std::make_unique<projectairsim::Logger>(callback), nullptr);

  try {
    auto unqptr = std::make_unique<projectairsim::Logger>(
        nullptr, projectairsim::LogLevel::kVerbose);
    FAIL();
  } catch (const std::invalid_argument& err) {
    EXPECT_STREQ("Invalid Argument : callback", err.what());
  }

  try {
    auto unqptr = std::make_unique<projectairsim::Logger>(nullptr);
    FAIL();
  } catch (const std::invalid_argument& err) {
    EXPECT_STREQ("Invalid Argument : callback", err.what());
  }
}

TEST(Logger, LogFatal) {
  // General description:
  // Verifies log fatal for Logger.
  // Arrange: prepare context for `TestLog(projectairsim::LogLevel::kFatal,`.
  TestLog(projectairsim::LogLevel::kFatal,
          [](projectairsim::Logger& logger, std::string component,
             const char* format) { logger.LogFatal(component, format); });

  TestLog(
      projectairsim::LogLevel::kFatal,
         // Act: run `[](projectairsim::Logger& logger, std::string component, const char* format,`.
      [](projectairsim::Logger& logger, std::string component, const char* format,
         int value) { logger.LogFatal(component, format, value); });
  // Assert: check result from `}`.
}

TEST(Logger, LogError) {
  // General description:
  // Verifies log error for Logger.
  // Arrange: prepare context for `TestLog(projectairsim::LogLevel::kError,`.
  TestLog(projectairsim::LogLevel::kError,
          [](projectairsim::Logger& logger, std::string component,
             const char* format) { logger.LogError(component, format); });

  TestLog(
      projectairsim::LogLevel::kError,
         // Act: run `[](projectairsim::Logger& logger, std::string component, const char* format,`.
      [](projectairsim::Logger& logger, std::string component, const char* format,
         int value) { logger.LogError(component, format, value); });
  // Assert: check result from `}`.
}

TEST(Logger, LogWarning) {
  // General description:
  // Verifies log warning for Logger.
  // Arrange: prepare context for `TestLog(projectairsim::LogLevel::kWarning,`.
  TestLog(projectairsim::LogLevel::kWarning,
          [](projectairsim::Logger& logger, std::string component,
             const char* format) { logger.LogWarning(component, format); });

  TestLog(
      projectairsim::LogLevel::kWarning,
         // Act: run `[](projectairsim::Logger& logger, std::string component, const char* format,`.
      [](projectairsim::Logger& logger, std::string component, const char* format,
         int value) { logger.LogWarning(component, format, value); });
  // Assert: check result from `}`.
}

TEST(Logger, LogTrace) {
  // General description:
  // Verifies log trace for Logger.
  // Arrange: prepare context for `TestLog(projectairsim::LogLevel::kTrace,`.
  TestLog(projectairsim::LogLevel::kTrace,
          [](projectairsim::Logger& logger, std::string component,
             const char* format) { logger.LogTrace(component, format); });

  TestLog(
      projectairsim::LogLevel::kTrace,
         // Act: run `[](projectairsim::Logger& logger, std::string component, const char* format,`.
      [](projectairsim::Logger& logger, std::string component, const char* format,
         int value) { logger.LogTrace(component, format, value); });
  // Assert: check result from `}`.
}

TEST(Logger, LogVerbose) {
  // General description:
  // Verifies log verbose for Logger.
  // Arrange: prepare context for `TestLog(projectairsim::LogLevel::kVerbose,`.
  TestLog(projectairsim::LogLevel::kVerbose,
          [](projectairsim::Logger& logger, std::string component,
             const char* format) { logger.LogVerbose(component, format); });

  TestLog(
      projectairsim::LogLevel::kVerbose,
      [](projectairsim::Logger& logger, std::string component, const char* format,
         int value) { logger.LogVerbose(component, format, value); });

  int count = 0;
                      // Act: run `auto callback = [&](const std::string& component, projectairsim::LogLevel level,`.
  auto callback = [&](const std::string& component, projectairsim::LogLevel level,
                      const std::string& message) {
    // Assert: check result from `EXPECT_EQ(message, "");`.
    EXPECT_EQ(message, "");
    count++;
  };

  projectairsim::Logger logger(callback, projectairsim::LogLevel::kVerbose);

  try {
    logger.LogVerbose("", "apple");
    FAIL();
  } catch (const std::invalid_argument& err) {
    EXPECT_STREQ("Invalid Argument : component", err.what());
  }

  try {
    logger.LogVerbose("test", nullptr);
    FAIL();
  } catch (const std::invalid_argument& err) {
    EXPECT_STREQ("Invalid Argument : format", err.what());
  }

  try {
    logger.LogVerbose("test", nullptr, 10);
    FAIL();
  } catch (const std::invalid_argument& err) {
    EXPECT_STREQ("Invalid Argument : format", err.what());
  }

  count = 0;
  logger.LogVerbose("test", "");
  EXPECT_EQ(count, 1);
}

TEST(Logger, GetLogLevel) {
  // General description:
  // Verifies get log level for Logger.
  // Arrange: prepare context for `auto callback = [](const std::string& component, projectairsim::LogLevel level,`.
  auto callback = [](const std::string& component, projectairsim::LogLevel level,
                     const std::string& message) {};
  // Act: run `projectairsim::Logger logger(callback);`.
  projectairsim::Logger logger(callback);

  // Assert: check result from `EXPECT_EQ(logger.GetLogLevel(), projectairsim::LogLevel::kError);`.
  EXPECT_EQ(logger.GetLogLevel(), projectairsim::LogLevel::kError);

  logger.SetLogLevel(projectairsim::LogLevel::kFatal);
  EXPECT_EQ(logger.GetLogLevel(), projectairsim::LogLevel::kFatal);

  logger.SetLogLevel(projectairsim::LogLevel::kError);
  EXPECT_EQ(logger.GetLogLevel(), projectairsim::LogLevel::kError);

  logger.SetLogLevel(projectairsim::LogLevel::kWarning);
  EXPECT_EQ(logger.GetLogLevel(), projectairsim::LogLevel::kWarning);

  logger.SetLogLevel(projectairsim::LogLevel::kTrace);
  EXPECT_EQ(logger.GetLogLevel(), projectairsim::LogLevel::kTrace);

  logger.SetLogLevel(projectairsim::LogLevel::kVerbose);
  EXPECT_EQ(logger.GetLogLevel(), projectairsim::LogLevel::kVerbose);
}

TEST(Logger, SetLogLevel) {
  // General description:
  // Verifies set log level for Logger.
  // Arrange: prepare context for `int count = 0;`.
  int count = 0;

  auto callback = [&](const std::string& component, projectairsim::LogLevel level,
                      const std::string& message) { count++; };

  projectairsim::Logger logger(callback, projectairsim::LogLevel::kVerbose);

  logger.SetLogLevel(projectairsim::LogLevel::kFatal);
  count = 0;
  // Act: run `logger.LogFatal("test", "message");`.
  logger.LogFatal("test", "message");
  // Assert: check result from `EXPECT_EQ(count, 1);`.
  EXPECT_EQ(count, 1);
  count = 0;
  logger.LogError("test", "message");
  EXPECT_EQ(count, 0);
  logger.LogWarning("test", "message");
  EXPECT_EQ(count, 0);
  logger.LogTrace("test", "message");
  EXPECT_EQ(count, 0);
  logger.LogVerbose("test", "message");
  EXPECT_EQ(count, 0);

  logger.SetLogLevel(projectairsim::LogLevel::kError);
  count = 0;
  logger.LogFatal("test", "message");
  EXPECT_EQ(count, 1);
  count = 0;
  logger.LogError("test", "message");
  EXPECT_EQ(count, 1);
  count = 0;
  logger.LogWarning("test", "message");
  EXPECT_EQ(count, 0);
  logger.LogTrace("test", "message");
  EXPECT_EQ(count, 0);
  logger.LogVerbose("test", "message");
  EXPECT_EQ(count, 0);

  logger.SetLogLevel(projectairsim::LogLevel::kWarning);
  count = 0;
  logger.LogFatal("test", "message");
  EXPECT_EQ(count, 1);
  count = 0;
  logger.LogError("test", "message");
  EXPECT_EQ(count, 1);
  count = 0;
  logger.LogWarning("test", "message");
  EXPECT_EQ(count, 1);
  count = 0;
  logger.LogTrace("test", "message");
  EXPECT_EQ(count, 0);
  logger.LogVerbose("test", "message");
  EXPECT_EQ(count, 0);

  logger.SetLogLevel(projectairsim::LogLevel::kTrace);
  count = 0;
  logger.LogFatal("test", "message");
  EXPECT_EQ(count, 1);
  count = 0;
  logger.LogError("test", "message");
  EXPECT_EQ(count, 1);
  count = 0;
  logger.LogWarning("test", "message");
  EXPECT_EQ(count, 1);
  count = 0;
  logger.LogTrace("test", "message");
  EXPECT_EQ(count, 1);
  count = 0;
  logger.LogVerbose("test", "message");
  EXPECT_EQ(count, 0);

  logger.SetLogLevel(projectairsim::LogLevel::kVerbose);
  count = 0;
  logger.LogFatal("test", "message");
  EXPECT_EQ(count, 1);
  count = 0;
  logger.LogError("test", "message");
  EXPECT_EQ(count, 1);
  count = 0;
  logger.LogWarning("test", "message");
  EXPECT_EQ(count, 1);
  count = 0;
  logger.LogTrace("test", "message");
  EXPECT_EQ(count, 1);
  count = 0;
  logger.LogVerbose("test", "message");
  EXPECT_EQ(count, 1);
}

void TestLog(projectairsim::LogLevel test_level,
             std::function<void(projectairsim::Logger&, std::string, const char*)>
                 log_func) {
  int count = 0;
  std::string actual_component;
  std::string actual_message;

  auto callback = [&](const std::string& component, projectairsim::LogLevel level,
                      const std::string& message) {
    if (level == test_level) {
      count++;
      actual_component = component;
      actual_message = message;
    }
  };

  projectairsim::Logger logger(callback, projectairsim::LogLevel::kVerbose);
  logger.SetLogLevel(test_level);

  count = 0;
  actual_component = "";
  actual_message = "";
  log_func(logger, "test", "message");
  EXPECT_EQ(count, 1);
  EXPECT_EQ("test", actual_component);
  EXPECT_EQ("message", actual_message);
}

void TestLog(
    projectairsim::LogLevel test_level,
    std::function<void(projectairsim::Logger&, std::string, const char*, int)>
        log_func) {
  int count = 0;
  std::string actual_component;
  std::string actual_message;

  auto callback = [&](const std::string& component, projectairsim::LogLevel level,
                      const std::string& message) {
    if (level == test_level) {
      count++;
      actual_component = component;
      actual_message = message;
    }
  };

  projectairsim::Logger logger(callback, projectairsim::LogLevel::kVerbose);
  logger.SetLogLevel(test_level);

  count = 0;
  actual_component = "";
  actual_message = "";
  log_func(logger, "test", "message %d", 124);
  EXPECT_EQ(count, 1);
  EXPECT_EQ("test", actual_component);
  EXPECT_EQ("message 124", actual_message);
}
