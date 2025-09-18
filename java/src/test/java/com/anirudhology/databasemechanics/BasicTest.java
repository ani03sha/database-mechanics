package com.anirudhology.databasemechanics;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.Test;

/**
 * Basic test to verify the project setup works correctly.
 */
class BasicTest {

  @Test
  void testBasicSetup() {
    // Simple test to verify JUnit 5 and AssertJ are working
    String projectName = "database-mechanics-java";
    assertThat(projectName).isNotNull().contains("database");
  }

  @Test
  void testAssertJ() {
    // Test that AssertJ assertions work correctly
    assertThat(2 + 2)
        .isEqualTo(4)
        .isGreaterThan(3)
        .isLessThan(5);
  }
}