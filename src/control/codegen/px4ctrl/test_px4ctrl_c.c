#include <math.h>
#include <stdio.h>

#include "px4ctrl_graphical_generated_shared.h"

#define INPUT_COUNT 17
#define OUTPUT_COUNT 8
#define FIXTURE_COUNT 4
#define TOLERANCE 1.0e-12

typedef struct {
  double input[INPUT_COUNT];
  double expected[OUTPUT_COUNT];
} Fixture;

/* Fixed sequence mirrored from raw/runtime_schema.json in the SIL evidence. */
static const Fixture kFixtures[FIXTURE_COUNT] = {
  {{1.2, -0.4, 0.3, -0.1, 0.05, -0.8, 0.25, -0.2, 0.15, -0.04,
    1.7, 0.9, 0.1, -0.05, 0.02, 0.35, -0.12},
   {3.0500000000000003, -2.14, 11.25165, 0.3116350556237367,
    0.2173306344398791, -0.12, 11.25165, 0.424519127326865}},
  {{-0.6, 0.3, -0.2, 0.14, -0.06, 0.7, -0.5, 0.18, -0.09, 0.08,
    0.4, 0.65, -0.12, 0.07, -0.03, -0.55, 0.27},
   {-1.92, 2.285, 9.11665, -0.09630802092040658,
    -0.288700769422872, 0.27, 9.11665, 0.3439666450826735}},
  {{0.15, 0.2, 0.0, 0.04, 0.11, 0.3, 0.1, 0.05, -0.03, -0.09,
    1.0, 1.25, 0.2, 0.1, 0.04, 0.9, 0.0},
   {-0.02500000000000001, 0.32999999999999996, 9.621649999999999,
    -0.022914498046734236, 0.024774783536712627, 0.0,
    9.621649999999999, 0.3630200425221661}},
  {{0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0},
   {0.0, 0.0, 9.80665, 0.0, 0.0, 0.0, 9.80665, 0.37}}
};

static int check_close(size_t fixture_index, size_t output_index,
                       double actual, double expected) {
  const double error = fabs(actual - expected);
  if (error <= TOLERANCE) {
    return 0;
  }
  fprintf(stderr,
          "fixture %zu output %zu: expected %.17g, got %.17g, error %.17g\n",
          fixture_index, output_index, expected, actual, error);
  return 1;
}

int main(void) {
  size_t fixture_index;

  for (fixture_index = 0; fixture_index < FIXTURE_COUNT; ++fixture_index) {
    const double *input = kFixtures[fixture_index].input;
    double output[OUTPUT_COUNT];
    size_t output_index;

    MosimPx4ctrlGeneratedGraphStepScalar(
      input[0], input[1], input[2], input[3], input[4], input[5], input[6],
      input[7], input[8], input[9], input[10], input[11], input[12],
      input[13], input[14], input[15], input[16],
      &output[0], &output[1], &output[2], &output[3], &output[4],
      &output[5], &output[6], &output[7]);

    for (output_index = 0; output_index < OUTPUT_COUNT; ++output_index) {
      if (check_close(fixture_index, output_index, output[output_index],
                      kFixtures[fixture_index].expected[output_index])) {
        return 1;
      }
    }
  }

  puts("px4ctrl generated C fixed-vector test passed");
  return 0;
}
