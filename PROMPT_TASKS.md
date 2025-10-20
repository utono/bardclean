# bardclean - Task File Generation Prompt
<!-- File: /home/mlj/utono/bardclean/PROMPT_TASKS.md -->

## File Generation Instructions

Important: Each TASKS-##.md file should be ≤ 300 lines.

The TASKS-##.md files are focused lists of development and implementation tasks
for specific milestones, based on:

- PRD.md (product requirements, functional requirements, success criteria)
- planning.md (algorithm design, implementation phases, technical decisions)
- bardclean.py (current implementation, existing functionality)
- Shakespeare file structure requirements (plays, narrative poems, poetry)

REQUIREMENTS:

1. Task Format & Hierarchical Numbering:
   - Each task must use "- [M.P.T] [ ] " format (Milestone.Phase.Task numbering)
   - Examples: "- [1.1.3] [ ] Implement file type detection function",
     "- [2.4.7] [X] Add JSON output schema"
   - Enables easy task references: "Implement task 3.2.5" or
     "Complete tasks 1.1.1-1.1.8"
   - Supports progress tracking: "Core Features: 15/23 tasks completed"

2. Organization Structure:
   - Milestones: Major development phases (1-4) with time estimates
   - Phases: Feature components within milestones (1.1, 1.2, 1.3...)
   - Tasks: Individual actionable development items with hierarchical
     numbering [M.P.T]
   - Sub-tasks: Use letters (a, b, c) for nested items under main tasks

3. Task Descriptions:
   - Include specific implementation requirements from PRD.md
   - Reference exact function names, class methods, and patterns from
     bardclean.py
   - Include test cases and verification steps for each feature
   - Add edge case handling and error scenarios
   - Include documentation requirements for new features

4. Cross-References: Reference specific requirements (FR-1, FR-2, etc.) from
   PRD.md, algorithms from planning.md, and existing code in bardclean.py

5. Timeline Estimates: Include estimated time ranges for major milestones based
   on complexity and dependencies

6. Priority Indicators: Mark critical path features and dependencies clearly,
   especially file type safety features

7. Technical Details: Include specific regex patterns, exit codes, JSON schemas,
   and function signatures from requirements

8. Success Criteria: Embed measurable outcomes and test coverage requirements
   from PRD success metrics in task descriptions

CONTENT TO INCLUDE:
- Core functionality improvements (dialogue detection, punctuation processing)
- File type detection system (plays vs narrative poems vs pure poetry)
- Safety features (block poetry processing, validation mode)
- Agent integration (JSON output, exit codes, programmatic API)
- Command-line interface enhancements (--json, --validate, --dry-run)
- Testing infrastructure (unit tests, integration tests, file fixtures)
- Documentation (shakespeare_file_structure.md, agent_usage.md, API docs)
- Performance optimization (processing speed, memory usage)
- Error handling (graceful failures, helpful error messages)

OUTPUT FORMAT:
- Use markdown with proper heading hierarchy (##, ###, ####)
- Regular text (outside code blocks) must wrap at 80 characters per line
- Code blocks can exceed 80 characters when necessary
- Minimize markdown formatting: Avoid bold/italic except for section headers
- Sub-tasks use plain letter prefixes (a. b. c.) without bold markup
- Apply [M.P.T] format to ALL checkbox tasks
- Enable easy completion percentage calculation per milestone/phase
- Mark tasks that require external dependencies (fzf, pytest, etc.)
- Note tasks requiring specific test files or fixtures
- Include prioritized implementation order at end:
  - Critical safety features (Priority 1) - file type detection, poetry blocking
  - Core enhancements (Priority 2) - JSON output, validation mode
  - Advanced features (Priority 3) - library API, statistics
- Add timeline summary and dependency graph with total task counts
- Ensure each "- [M.P.T] [ ] " task is actionable and testable
- Task Reference Benefits:
  - Easy communication: "Please implement feature task 2.3.4"
  - Progress reports: "Agent integration is 75% complete (12/16 tasks done)"
  - Dependency tracking: "Task 3.2.1 requires completion of 1.2.5
    (file type detection)"
  - Development planning: "Milestone 2 contains 34 tasks across 4 phases"

## COMPREHENSIVE TASK FILE BREAKDOWN:

### TASKS-01.md: Core Functionality & File Type Safety (Milestone 1)
- Phase 1.1: File Type Detection (FR-1 from PRD.md)
- Phase 1.2: Dialogue Processing Improvements (enhance existing algorithm)
- Phase 1.3: Poetry Protection (FR-4 from PRD.md)
- Critical Path: Prevents destructive processing of sonnets and lyric poems
- Implementation Focus: Detection patterns, validation logic, safety checks
- Estimated time: 8-12 hours
- Key outputs: File type classifier, validation mode, protection mechanisms

### TASKS-02.md: Command-Line Interface & Validation (Milestone 2)
- Phase 2.1: Argument Parser Enhancement (FR-7 from PRD.md)
- Phase 2.2: Validation Mode (FR-9 from PRD.md)
- Phase 2.3: Dry-Run Preview (enable preview without modification)
- Phase 2.4: Exit Code Standardization (FR-10 from PRD.md)
- Implementation Focus: CLI design, user feedback, error handling
- Estimated time: 6-10 hours
- Key outputs: Enhanced CLI, validation output, exit code system

### TASKS-03.md: Agent Integration & JSON Output (Milestone 3)
- Phase 3.1: JSON Output Schema (FR-8 from PRD.md)
- Phase 3.2: Programmatic API Design (Phase 3 from planning.md)
- Phase 3.3: Batch Processing Safety (auto-detect and filter by type)
- Phase 3.4: Statistics & Metrics (punctuation counting, processing stats)
- Implementation Focus: Structured output, API design, automation safety
- Estimated time: 10-14 hours
- Key outputs: JSON schema, Python API, batch validation

### TASKS-04.md: Testing, Documentation & Polish (Milestone 4)
- Phase 4.1: Unit Test Suite (pattern matching, state transitions)
- Phase 4.2: Integration Tests (full file processing, edge cases)
- Phase 4.3: Documentation (shakespeare_file_structure.md, agent_usage.md)
- Phase 4.4: Performance & Optimization (speed, memory, reliability)
- Implementation Focus: Test coverage, documentation, polish
- Estimated time: 8-12 hours
- Key outputs: Test suite (≥80% coverage), complete docs, optimized code

EXAMPLE STRUCTURE (for each TASKS-##.md file):
```markdown
# bardclean - Core Functionality & File Type Safety
<!-- File: /home/mlj/utono/bardclean/TASKS-01.md -->

## Milestone 1: Core Functionality & File Type Safety (8-12 hours)

### Phase 1.1: File Type Detection (FR-1 from PRD.md)
- [1.1.1] [ ] Implement detect_file_type() function
  a. Add detection patterns for plays (character names, stage directions)
  b. Add detection patterns for sonnets (Roman numerals, 14-line structure)
  c. Add detection patterns for narrative poems (quoted dialogue, narrator tags)
  d. Return tuple: (file_type, confidence_score, features_dict)
- [1.1.2] [ ] Create FileTypeFeatures dataclass
  a. character_names: List[str]
  b. stage_direction_count: int
  c. act_scene_count: int
  d. quoted_dialogue_count: int
  e. roman_numeral_markers: List[str]
- [1.1.3] [ ] Add file type classification logic
  a. Play: has_character_names AND has_stage_directions
  b. Sonnet: has_roman_numerals AND NOT has_character_names
  c. Narrative: has_quoted_dialogue AND has_narrator_tags
  d. Lyric: NOT has_character_names AND NOT has_stage_directions
- [1.1.4] [ ] Implement confidence scoring algorithm
  a. Calculate based on feature strength and count
  b. Return 0.0-1.0 confidence score
  c. Warn if confidence < 0.8

### Phase 1.2: Dialogue Processing Improvements
- [1.2.1] [ ] Enhance character name detection pattern
  a. Verify CHAR_NAME_PATTERN handles all cases from planning.md
  b. Add length validation (< 30 chars as specified)
  c. Add ACT/SCENE exclusion logic
- [1.2.2] [ ] Improve state machine transitions
  a. Document all state transitions clearly
  b. Add state validation checks
  c. Test with edge cases from planning.md
- [1.2.3] [ ] Add punctuation statistics tracking
  a. Create PunctuationStats class
  b. Track counts per punctuation type
  c. Include in processing result

### Phase 1.3: Poetry Protection (FR-4 from PRD.md)
- [1.3.1] [ ] Implement poetry blocking by default
  a. Check file_type in ['sonnet', 'lyric_poem']
  b. Return error without --force flag
  c. Log warning even with --force
- [1.3.2] [ ] Create clear error messages for blocked files
  a. "File detected as 'sonnet' (pure poetry)"
  b. "Use --force to override (not recommended)"
  c. Explain why processing would be destructive
- [1.3.3] [ ] Add --force flag for override
  a. Parse in argument parser
  b. Check in validation logic
  c. Log override with warning

## Verification Checklist for Milestone 1:
- [ ] File type detection achieves ≥95% accuracy on known corpus
- [ ] All 38 plays detected correctly
- [ ] All 4+ poetry files blocked by default
- [ ] Poetry can be processed only with explicit --force
- [ ] Character name pattern matches all formats from planning.md
- [ ] State machine handles all edge cases
- [ ] Error messages are clear and actionable

## Testing Requirements:
- [ ] Unit tests for detect_file_type() with all file types
- [ ] Unit tests for character name pattern matching
- [ ] Integration tests with actual Shakespeare files
- [ ] Test poetry blocking mechanism
- [ ] Test --force override functionality
```

## IMPORTANT REQUIREMENTS FOR ALL TASK FILES:

1. File Type Safety Priority: Milestone 1 must prevent poetry damage before
   any other features
2. Line Limit: Each TASKS-##.md file must be ≤300 lines
3. PRD Alignment: Reference specific FR-## requirements from PRD.md
4. Cross-References: Link between requirements, planning decisions, and
   implementation tasks
5. Progress Tracking: Maintain hierarchical [M.P.T] numbering across all files
6. File Headers: Each file needs proper header with milestone name and file path
7. Test Coverage: Each phase must include test requirements and acceptance
   criteria
8. Documentation: Include documentation tasks for user-facing features

### Source Files to Reference in Tasks:

#### Core Implementation (in /home/mlj/utono/bardclean/):
- bardclean.py: Main script with DialogueProcessor class, state machine,
  pattern matching
- PRD.md: Product requirements (FR-1 through FR-10), success criteria,
  use cases
- planning.md: Algorithm design, pattern evolution, technical decisions,
  lessons learned
- README.md: User documentation, usage examples, features list

#### Requirements from PRD.md:
- FR-1: File Type Detection (plays, narrative poems, sonnets, lyric poems)
- FR-2: Dialogue Processing (state machine, pattern matching, punctuation
  removal)
- FR-3: Narrative Poem Processing (optional, quoted dialogue only)
- FR-4: Poetry Protection (block sonnets/lyrics, require --force)
- FR-5: File Permission Handling (read-only files, restore permissions)
- FR-6: Backup Creation (.bak files, inherit permissions)
- FR-7: Command-Line Interface (arguments, flags, help text)
- FR-8: JSON Output Format (structured data for agents)
- FR-9: Validation Mode (check structure before processing)
- FR-10: Exit Codes (0-7, standard error signaling)

#### Implementation Patterns from planning.md:
- State Machine: Initial → Dialogue → Initial transitions
- Character Name Detection: Pattern evolution from mixed-case to all-caps
- Permission Handling: Detect read-only, make writable, restore
- Punctuation Removal: Regex pattern with specific exclusions
- File Type Classification: Feature-based detection algorithm

#### Test Files to Create:
- tests/fixtures/test_play.txt: Minimal play structure
- tests/fixtures/test_narrative.txt: Narrative poem sample
- tests/fixtures/test_sonnet.txt: Sonnet sample
- tests/fixtures/test_lyric.txt: Lyric poem sample
- tests/test_dialogue_processor.py: Unit tests for core functionality
- tests/test_file_type_detection.py: File type classifier tests
- tests/test_cli.py: Command-line interface tests
- tests/test_integration.py: Full processing workflow tests

### Task File Dependencies:
- TASKS-02.md depends on completion of TASKS-01.md Phase 1.1 (file type
  detection)
- TASKS-03.md depends on completion of TASKS-02.md (CLI and validation ready)
- TASKS-04.md spans all previous milestones (testing everything)

### Critical Path Requirements:
- File type detection must be implemented before any batch processing features
- Poetry protection must be in place before public release
- JSON output must be implemented before agent integration
- Validation mode must exist before batch automation
- Test coverage must reach ≥80% before version 1.0 release
- Documentation must be complete before agent adoption

### Development Priorities:
1. **Critical (P0)**: File type detection, poetry blocking, safety features
2. **Important (P1)**: JSON output, validation mode, exit codes
3. **Nice-to-Have (P2)**: Library API, statistics, performance optimization

### Success Metrics from PRD.md:
- [ ] Correctly processes all 38 Shakespeare plays
- [ ] Blocks all 4+ pure poetry files by default
- [ ] Provides accurate file type detection (≥95% confidence)
- [ ] Creates backups for 100% of processed files
- [ ] Restores permissions on 100% of read-only files
- [ ] Provides JSON output for programmatic access
- [ ] Achieves ≥80% code coverage with tests
- [ ] Zero data loss incidents
- [ ] Zero poetry files incorrectly processed

Generate comprehensive task breakdowns that a developer could use to implement
the entire bardclean enhancement roadmap from scratch with full traceability,
progress tracking, and alignment to product requirements.
