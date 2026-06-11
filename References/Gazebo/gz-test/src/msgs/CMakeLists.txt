PROTOBUF_GENERATE_CPP(PROTO_PRIVATE_SRC PROTO_PRIVATE_HEADERS
artifact.proto
entrypoint.proto
iteration.proto
repository.proto
scenario.proto
suite.proto
test.proto
trigger.proto
value_objects.proto
)

set(PROTO_PRIVATE_SRC ${PROTO_PRIVATE_SRC} PARENT_SCOPE)
set(PROTO_PRIVATE_HEADERS ${PROTO_PRIVATE_HEADERS} PARENT_SCOPE)

add_custom_target(gz-test_private_msgs
  DEPENDS ${PROTO_PRIVATE_SRC}
)
