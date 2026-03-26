# Challenge 205: Cross-File Refactoring Consistency

## Objective

Rename `UserService` to `AccountService` and rename the `getUser` method to `getAccount` across a 25-file TypeScript codebase. Every single reference must be updated consistently.

## Input

`input/project/` contains a 25-file Express.js/TypeScript REST API for a task management application. `UserService` is referenced in at least 12 of these files through imports, type annotations, variable names, test mocks, route handlers, and middleware.

## Requirements

1. Rename the class `UserService` to `AccountService` everywhere
2. Rename the method `getUser` to `getAccount` everywhere
3. Rename the file `UserService.ts` to `AccountService.ts`
4. Update all import paths that reference `UserService`
5. Rename local variables: `userService` becomes `accountService`
6. Update all test mocks and type annotations
7. Do **NOT** rename the `User` model/interface (only the Service class)
8. All 25 original files must be present in the output
9. No new files should be created (except the renamed AccountService.ts replacing UserService.ts)

## Required Output

Place the complete refactored project in the output directory. Every file from the input must be present. The `UserService.ts` file should be renamed to `AccountService.ts`.

## Scoring

**Binary**: ALL verification tests must pass or score is 0. This tests the framework's ability to perform consistent cross-file refactoring without missing references or introducing inconsistencies.
