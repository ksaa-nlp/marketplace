# Test report: <feature name>

- **Spec:** `<path>` (version <x>, dated <date>)
- **Report date:** <YYYY-MM-DD>
- **Code state:** branch `<branch>`, commit `<short sha>`<, plus uncommitted changes>
- **Environment:** <what was available: database yes/no, app running yes/no>

## Verdict

<One short paragraph: ready or not, and the reasons that decide it.>

## Summary

|                        | Count |
| ---------------------- | ----- |
| Requirements extracted |       |
| Scenarios              |       |
| Pass                   |       |
| Fail                   |       |
| Not run                |       |

| Evidence  | Count |
| --------- | ----- |
| Automated |       |
| Partial   |       |
| Manual    |       |
| None      |       |

## Findings

### Failures

<For each: scenario ID, what was expected, what happened, the output.>

### Spec and code disagreements

<For each: spec section, what it says, what the code does, file reference.>

### Coverage gaps

<Scenarios with evidence None or Partial, most important first.>

## Scenarios

### <Area name>

| ID        | Requirement | Scenario                           | Expected result     | Evidence                                      | Result                  |
| --------- | ----------- | ---------------------------------- | ------------------- | --------------------------------------------- | ----------------------- |
| <AREA-01> | <§ ref>     | <preconditions and steps, briefly> | <observable result> | <Automated: file › test name / Manual / None> | <Pass / Fail / Not run> |

## Manual checklist

<Numbered, self-contained steps for every Manual scenario, grouped by role.
Each ends with the expected result and a checkbox.>

1. [ ] **<ID>** <steps> → <expected result>

## Excluded

<Items the spec marks deferred or out of scope, with the section reference.>

## Not verified

<Anything this report could not check and why.>
