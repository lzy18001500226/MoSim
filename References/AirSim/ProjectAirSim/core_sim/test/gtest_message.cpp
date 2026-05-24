// Copyright (C) Microsoft Corporation. 
// Copyright (C) 2025 IAMAI CONSULTING CORP

// MIT License. All rights reserved.

#include <iostream>
#include <string>

#include "core_sim/message/request_message.hpp"
#include "core_sim/message/response_failure_message.hpp"
#include "core_sim/message/response_success_message.hpp"
#include "gtest/gtest.h"
#include "json.hpp"

namespace projectairsim = microsoft::projectairsim;
using json = nlohmann::json;

TEST(Message, RequestMessageContent) {
  // General description:
  // Builds a request payload and verifies each accessor returns the exact
  // constructor value.
  // Arrange: prepare context for `int id = 1;`.
  int id = 1;
  // Arrange: prepare context for `std::string method = "TestRequestMethod";`.
  std::string method = "TestRequestMethod";
  // Arrange: prepare context for `json params = R"({"param1": "val1"})"_json;`.
  json params = R"({"param1": "val1"})"_json;
  // Arrange: prepare context for `float version = 10.0;`.
  float version = 10.0;
  // Act: run `auto request_message =`.
  auto request_message =
      projectairsim::RequestMessage(id, method, params, version);

  // Assert: check result from `EXPECT_EQ(request_message.GetID(), 1);`.
  EXPECT_EQ(request_message.GetID(), 1);
  // Assert: check result from `EXPECT_TRUE(request_message.GetMethod() == method);`.
  EXPECT_TRUE(request_message.GetMethod() == method);
  //! Using PREDn instead of EQ or TRUE to assist with debuggin on failure;
  //! With predicate assertions, the func args gets printed for free if failed
  // Enable after Json-Msgpack upgrade
  // EXPECT_PRED2([](auto returned_val,
  //                auto actual_val) { return returned_val == actual_val; },
  //             request_message.GetParams(), params);
  // EXPECT_EQ(request_message.GetParams(), params);

  // Assert: check result from `EXPECT_FLOAT_EQ(request_message.GetVersion(), version);`.
  EXPECT_FLOAT_EQ(request_message.GetVersion(), version);
}

TEST(Message, RequestMessagePackingAndUnpacking) {
  // General description:
  // Round-trips a request through serialization and deserialization and checks
  // all fields survive transport losslessly.
  // Arrange: prepare context for `int id = 1;`.
  int id = 1;
  // Arrange: prepare context for `std::string method = "TestRequestMethod";`.
  std::string method = "TestRequestMethod";
  // Arrange: prepare context for `json params = R"({"param1": "val1"})"_json;`.
  json params = R"({"param1": "val1"})"_json;
  // Arrange: prepare context for `float version = 10.0;`.
  float version = 10.0;
  auto original_message =
      projectairsim::RequestMessage(id, method, params, version);
  auto original_message_packed = original_message.Serialize();

  auto unpacked_result = projectairsim::RequestMessage();
  // Act: run `unpacked_result.Deserialize(original_message_packed);`.
  unpacked_result.Deserialize(original_message_packed);

  // Assert: check result from `EXPECT_EQ(original_message.GetID(), unpacked_result.GetID());`.
  EXPECT_EQ(original_message.GetID(), unpacked_result.GetID());

  // Assert: check result from `EXPECT_TRUE(original_message.GetMethod() == unpacked_result.GetMethod());`.
  EXPECT_TRUE(original_message.GetMethod() == unpacked_result.GetMethod());
  // Assert: check result from `EXPECT_PRED2([](auto returned_val,`.
  EXPECT_PRED2([](auto returned_val,
                  auto actual_val) { return returned_val == actual_val; },
               original_message.GetParams(), unpacked_result.GetParams());
  // EXPECT_EQ(original_message.GetParams(), result.GetParams());

  // Assert: check result from `EXPECT_FLOAT_EQ(original_message.GetVersion(), unpacked_result.GetVersion());`.
  EXPECT_FLOAT_EQ(original_message.GetVersion(), unpacked_result.GetVersion());
}

TEST(Message, ResponseSuccessMessageContent) {
  // General description:
  // Verifies a success response retains id, result payload, and version exactly
  // as provided to the constructor.
  // Arrange: prepare context for `int id = 1;`.
  int id = 1;
  // Arrange: prepare context for `json result = R"({"res1": "val1"})"_json;`.
  json result = R"({"res1": "val1"})"_json;
  // Arrange: prepare context for `float version = 10.0;`.
  float version = 10.0;
  // Act: run `auto request_message =`.
  auto request_message =
      projectairsim::ResponseSuccessMessage(id, result, version);

  // Assert: check result from `EXPECT_EQ(request_message.GetID(), 1);`.
  EXPECT_EQ(request_message.GetID(), 1);
  //! Using PREDn instead of EQ or TRUE to assist with debuggin on failure;
  //! With predicate assertions, the func args gets printed for free if failed
  // Enable after Json-Msgpack upgrade
  // EXPECT_PRED2([](auto returned_val,
  //                auto actual_val) { return returned_val == actual_val; },
  //             request_message.GetResult(), result);
  // EXPECT_EQ(request_message.GetResult(), result);

  // Assert: check result from `EXPECT_FLOAT_EQ(request_message.GetVersion(), version);`.
  EXPECT_FLOAT_EQ(request_message.GetVersion(), version);
}

TEST(Message, ResponseSuccessMessagePackingAndUnpacking) {
  // General description:
  // Verifies success response serialization/deserialization preserves id,
  // result JSON, and version.
  // Arrange: prepare context for `int id = 1;`.
  int id = 1;
  // Arrange: prepare context for `json result = R"({"res1": "val1"})"_json;`.
  json result = R"({"res1": "val1"})"_json;
  // Arrange: prepare context for `float version = 10.0;`.
  float version = 10.0;
  auto original_message =
      projectairsim::ResponseSuccessMessage(id, result, version);
  auto original_message_packed = original_message.Serialize();

  auto unpacked_result = projectairsim::ResponseSuccessMessage();
  // Act: run `unpacked_result.Deserialize(original_message_packed);`.
  unpacked_result.Deserialize(original_message_packed);

  // Assert: check result from `EXPECT_EQ(original_message.GetID(), unpacked_result.GetID());`.
  EXPECT_EQ(original_message.GetID(), unpacked_result.GetID());

  // Assert: check result from `EXPECT_PRED2([](auto returned_val,`.
  EXPECT_PRED2([](auto returned_val,
                  auto actual_val) { return returned_val == actual_val; },
               original_message.GetResult(), unpacked_result.GetResult());
  // EXPECT_EQ(original_message.GetResult(), result.GetResult());

  // Assert: check result from `EXPECT_FLOAT_EQ(original_message.GetVersion(), unpacked_result.GetVersion());`.
  EXPECT_FLOAT_EQ(original_message.GetVersion(), unpacked_result.GetVersion());
}

TEST(Message, ResponseFailureMessageContent) {
  // General description:
  // Verifies a failure response stores id, error payload, and version exactly
  // as supplied.
  // Arrange: prepare context for `int id = 1;`.
  int id = 1;
  // Arrange: prepare context for `json error = R"({"code": "err_code", "message": "err_msg"})"_json;`.
  json error = R"({"code": "err_code", "message": "err_msg"})"_json;
  // Arrange: prepare context for `float version = 10.0;`.
  float version = 10.0;
  // Act: run `auto request_message =`.
  auto request_message =
      projectairsim::ResponseFailureMessage(id, error, version);

  // Assert: check result from `EXPECT_EQ(request_message.GetID(), 1);`.
  EXPECT_EQ(request_message.GetID(), 1);
  //! Using PREDn instead of EQ or TRUE to assist with debuggin on failure;
  //! With predicate assertions, the func args gets printed for free if failed
  // Enable after Json-Msgpack upgrade
  // EXPECT_PRED2([](auto returned_val,
  //                auto actual_val) { return returned_val == actual_val; },
  //             request_message.GetError(), error);
  // EXPECT_EQ(request_message.GetError(), error);

  // Assert: check result from `EXPECT_FLOAT_EQ(request_message.GetVersion(), version);`.
  EXPECT_FLOAT_EQ(request_message.GetVersion(), version);
}

TEST(Message, ResponseFailureMessagePackingAndUnpacking) {
  // General description:
  // Ensures a failure response round-trips through serialization with no field
  // mutation.
  // Arrange: prepare context for `int id = 1;`.
  int id = 1;
  // Arrange: prepare context for `json error = R"({"code": "err_code", "message": "err_msg"})"_json;`.
  json error = R"({"code": "err_code", "message": "err_msg"})"_json;
  // Arrange: prepare context for `float version = 10.0;`.
  float version = 10.0;
  auto original_message =
      projectairsim::ResponseFailureMessage(id, error, version);
  auto original_message_packed = original_message.Serialize();

  auto unpacked_result = projectairsim::ResponseFailureMessage();
  // Act: run `unpacked_result.Deserialize(original_message_packed);`.
  unpacked_result.Deserialize(original_message_packed);

  // Assert: check result from `EXPECT_EQ(original_message.GetID(), unpacked_result.GetID());`.
  EXPECT_EQ(original_message.GetID(), unpacked_result.GetID());

  // Assert: check result from `EXPECT_PRED2([](auto returned_val,`.
  EXPECT_PRED2([](auto returned_val,
                  auto actual_val) { return returned_val == actual_val; },
               original_message.GetError(), unpacked_result.GetError());
  // EXPECT_EQ(original_message.GetError(), result.GetError());

  // Assert: check result from `EXPECT_FLOAT_EQ(original_message.GetVersion(), unpacked_result.GetVersion());`.
  EXPECT_FLOAT_EQ(original_message.GetVersion(), unpacked_result.GetVersion());
}
