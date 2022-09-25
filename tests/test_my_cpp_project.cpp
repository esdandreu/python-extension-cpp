#include <gtest/gtest.h>
#include "my_cpp_project.hpp"

TEST(AddTest, PositiveNumbers) {
  EXPECT_EQ(3, add(1, 2));
}

TEST(AddTest, NegativeNumbers) {
  EXPECT_EQ(3, add(5, -2));
}

TEST(AddTest, HandleZeros) {
  EXPECT_EQ(3, add(3, 0));
}