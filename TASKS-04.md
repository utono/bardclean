# bardclean - Testing, Documentation & Polish
<!-- File: /home/mlj/utono/bardclean/TASKS-04.md -->

## Milestone 4: Testing, Documentation & Polish (8-12 hours)

This milestone ensures production-readiness through comprehensive testing,
documentation, and final polish. This is required before version 1.0 release
and public agent adoption.

**Priority:** P1 (Important - Required for production release)

**Dependencies:**
- All previous milestones (1, 2, 3) must be substantially complete
- Requires working implementations to test against

**Deliverables:**
- Comprehensive test suite (≥80% coverage)
- Complete user and agent documentation
- Performance optimizations
- Production-ready release

---

## Phase 4.1: Unit Test Suite

### Overview
Create comprehensive unit tests covering pattern matching, state machine logic,
file type detection, and all core functionality.

**Estimated time:** 4-5 hours

### Tasks

- [4.1.1] [ ] Set up testing infrastructure
  a. Create tests/ directory structure
  b. Create tests/fixtures/ for test data
  c. Install pytest: pip install pytest pytest-cov
  d. Create pytest.ini configuration
  e. Create conftest.py with fixtures
  f. Add .gitignore for test outputs

- [4.1.2] [ ] Create test fixtures
  a. Create tests/fixtures/test_play.txt (minimal play)
  b. Create tests/fixtures/test_sonnet.txt (minimal sonnet)
  c. Create tests/fixtures/test_narrative.txt (narrative poem)
  d. Create tests/fixtures/test_lyric.txt (lyric poem)
  e. Create tests/fixtures/test_invalid.txt (non-Shakespeare)
  f. Add fixtures with various character name formats

- [4.1.3] [ ] Test pattern matching
  a. Create tests/test_patterns.py
  b. Test CHAR_NAME_PATTERN with all formats
  c. Test mixed case names: "Ber.", "Hor."
  d. Test ALL CAPS names: "HAMLET.", "OPHELIA."
  e. Test multi-word names: "First Musician.", "Lady Macbeth."
  f. Test exclusions: "ACT I.", "SCENE II."
  g. Test edge cases: empty string, very long names

- [4.1.4] [ ] Test stage direction detection
  a. Test STAGE_DIR_PATTERN matching
  b. Test: "[Enter HAMLET]", "[Exit]", "[Aside]"
  c. Test variations: "[Thunder and lightning]"
  d. Test negative cases: "(aside)", "Enter HAMLET"
  e. Verify no false positives

- [4.1.5] [ ] Test punctuation removal
  a. Create tests/test_punctuation.py
  b. Test removal: commas, semicolons, colons
  c. Test removal: exclamations, quotes, dashes
  d. Test preservation: periods, questions, apostrophes
  e. Test edge cases: multiple punctuation, only punctuation
  f. Verify counts are accurate

- [4.1.6] [ ] Test state machine transitions
  a. Create tests/test_state_machine.py
  b. Test Initial → Dialogue on character name
  c. Test Dialogue → Initial on blank line
  d. Test Dialogue → Initial on stage direction
  e. Test staying in Dialogue on dialogue line
  f. Test staying in Initial on metadata
  g. Test edge cases: empty file, no dialogue

- [4.1.7] [ ] Test file type detection
  a. Create tests/test_file_type.py
  b. Test play detection with test_play.txt
  c. Test sonnet detection with test_sonnet.txt
  d. Test narrative detection with test_narrative.txt
  e. Test lyric detection with test_lyric.txt
  f. Test confidence scores
  g. Test with real Shakespeare files

- [4.1.8] [ ] Test feature extraction
  a. Test extract_features() with each file type
  b. Verify character names extracted
  c. Verify stage direction count
  d. Verify act/scene count
  e. Verify quoted dialogue detection
  f. Verify Roman numeral detection

- [4.1.9] [ ] Run coverage analysis
  a. Run: pytest --cov=bardclean tests/
  b. Generate coverage report
  c. Identify untested code paths
  d. Add tests to reach ≥80% coverage
  e. Focus on critical paths first

### Verification Checklist
- [ ] pytest runs without errors
- [ ] All pattern tests pass
- [ ] State machine tests cover all transitions
- [ ] File type detection tests pass
- [ ] Code coverage ≥ 80%
- [ ] All edge cases covered
- [ ] Tests run in < 5 seconds

---

## Phase 4.2: Integration Tests

### Overview
Create integration tests that verify end-to-end workflows with actual file
processing, including CLI integration and error scenarios.

**Estimated time:** 3-4 hours

### Tasks

- [4.2.1] [ ] Set up integration test framework
  a. Create tests/integration/ directory
  b. Create test file copies (don't modify originals)
  c. Set up temporary directories for output
  d. Create cleanup fixtures
  e. Add integration test markers

- [4.2.2] [ ] Test full file processing
  a. Create tests/integration/test_processing.py
  b. Test processing test_play.txt end-to-end
  c. Verify backup created
  d. Verify permissions restored
  e. Verify output file correctness
  f. Verify statistics accuracy
  g. Clean up after test

- [4.2.3] [ ] Test CLI argument handling
  a. Create tests/integration/test_cli.py
  b. Test --validate flag
  c. Test --dry-run flag
  d. Test --json flag
  e. Test --force flag
  f. Test argument combinations
  g. Use subprocess.run() to test CLI

- [4.2.4] [ ] Test poetry blocking
  a. Test sonnet file blocked without --force
  b. Test lyric file blocked without --force
  c. Test error message correctness
  d. Test --force override works
  e. Verify warning logged with --force

- [4.2.5] [ ] Test batch processing
  a. Test processing multiple plays
  b. Test mixed file types (plays + poetry)
  c. Test --safe-batch filtering
  d. Test --continue-on-error
  e. Verify batch statistics
  f. Test JSON output for batch

- [4.2.6] [ ] Test error scenarios
  a. Test file not found
  b. Test permission denied
  c. Test invalid file format
  d. Test corrupted file
  e. Verify exit codes correct
  f. Verify error messages helpful

- [4.2.7] [ ] Test JSON output validation
  a. Parse JSON output with json.loads()
  b. Verify schema matches specification
  c. Check all required fields present
  d. Verify data types correct
  e. Test with validation mode
  f. Test with processing mode

- [4.2.8] [ ] Test validation mode
  a. Test --validate with each file type
  b. Verify no files modified
  c. Verify ValidationResult accuracy
  d. Test confidence scores
  e. Test recommendation text
  f. Test JSON output format

- [4.2.9] [ ] Test real Shakespeare files
  a. Test with hamlet_gut.txt (if available)
  b. Test with sonnets_gut.txt (should block)
  c. Verify results match expected
  d. Use copies, not originals
  e. Validate processing statistics

### Verification Checklist
- [ ] All integration tests pass
- [ ] End-to-end workflows work correctly
- [ ] CLI arguments work as expected
- [ ] Error handling is robust
- [ ] JSON output is valid
- [ ] Real files process correctly
- [ ] No test pollution (files cleaned up)

---

## Phase 4.3: Documentation Completion

### Overview
Complete all user-facing and developer documentation to production quality,
including comprehensive guides and troubleshooting.

**Estimated time:** 3-4 hours

### Tasks

- [4.3.1] [ ] Complete shakespeare_file_structure.md
  a. Document play structure with examples
  b. Document sonnet structure
  c. Document narrative poem structure
  d. Document lyric poem structure
  e. Add detection criteria table
  f. Include visual examples
  g. Add character name format variations

- [4.3.2] [ ] Complete agent_usage.md (if not done in 3.5)
  a. Add comprehensive JSON schema documentation
  b. Document all API functions
  c. Add workflow examples
  d. Include error handling patterns
  e. Add best practices section
  f. Include troubleshooting guide

- [4.3.3] [ ] Update README.md
  a. Add all new features and flags
  b. Update installation instructions
  c. Add comprehensive usage examples
  d. Document --json, --validate, --dry-run flags
  e. Add troubleshooting section
  f. Update feature list
  g. Add links to detailed docs

- [4.3.4] [ ] Create CONTRIBUTING.md
  a. Add development setup instructions
  b. Document testing procedures
  c. Add code style guidelines
  d. Include pull request template
  e. Add issue reporting guidelines

- [4.3.5] [ ] Create API_REFERENCE.md
  a. Document all public functions
  b. Include type signatures
  c. Add usage examples for each function
  d. Document exceptions
  e. Add programmatic usage guide

- [4.3.6] [ ] Add docstrings to all code
  a. Add module-level docstrings
  b. Add class docstrings
  c. Add method docstrings with parameters
  d. Document return types
  e. Include usage examples in docstrings
  f. Use Google or NumPy docstring style

- [4.3.7] [ ] Create CHANGELOG.md
  a. Document version 1.0 features
  b. List all implemented features
  c. Note breaking changes (if any)
  d. Add migration guide (if needed)
  e. Use Keep a Changelog format

- [4.3.8] [ ] Add inline code comments
  a. Comment complex algorithms
  b. Explain state machine transitions
  c. Document regex patterns
  d. Clarify file type detection logic
  e. Keep comments concise and useful

### Verification Checklist
- [ ] All documentation files created
- [ ] README.md is comprehensive
- [ ] shakespeare_file_structure.md is complete
- [ ] agent_usage.md has all examples
- [ ] All code has docstrings
- [ ] Documentation is well-formatted
- [ ] Links between docs work correctly

---

## Phase 4.4: Performance & Optimization

### Overview
Optimize processing speed, memory usage, and overall performance for
production use with large files and batches.

**Estimated time:** 2-3 hours

### Tasks

- [4.4.1] [ ] Add performance benchmarking
  a. Create benchmark script
  b. Test with various file sizes
  c. Test with 38 play batch
  d. Measure lines per second
  e. Identify bottlenecks
  f. Document baseline performance

- [4.4.2] [ ] Optimize file reading
  a. Use efficient file reading method
  b. Consider line-by-line for large files
  c. Avoid loading entire file if possible
  d. Test memory usage with large files
  e. Implement chunked reading if needed

- [4.4.3] [ ] Optimize regex patterns
  a. Review all regex patterns
  b. Pre-compile all patterns (already done?)
  c. Simplify patterns if possible
  d. Test pattern performance
  e. Use non-capturing groups where appropriate

- [4.4.4] [ ] Optimize batch processing
  a. Minimize redundant operations
  b. Reuse compiled patterns
  c. Consider caching file type detection
  d. Optimize statistics collection
  e. Test batch performance

- [4.4.5] [ ] Add progress indicators for large batches
  a. Show progress bar with tqdm (optional)
  b. Display current file being processed
  c. Show completion percentage
  d. Estimate time remaining
  e. Make optional with --progress flag

- [4.4.6] [ ] Test with large files
  a. Test with files > 10,000 lines
  b. Monitor memory usage
  c. Verify processing speed acceptable
  d. Check for memory leaks
  e. Ensure ≤ 5 seconds per MB

### Verification Checklist
- [ ] Processing speed meets requirements (< 5s per 1MB)
- [ ] Memory usage is reasonable
- [ ] Batch processing is efficient
- [ ] No memory leaks detected
- [ ] Performance benchmarks documented
- [ ] Progress indicators work (if implemented)

---

## Phase 4.5: Production Polish & Release Prep

### Overview
Final polish, quality checks, and release preparation for version 1.0.

**Estimated time:** 1-2 hours

### Tasks

- [4.5.1] [ ] Code quality review
  a. Run type checker: mypy bardclean.py
  b. Run linter: pylint or flake8
  c. Fix any warnings
  d. Ensure consistent code style
  e. Remove debug print statements
  f. Remove commented-out code

- [4.5.2] [ ] Error message review
  a. Review all error messages
  b. Ensure messages are helpful
  c. Add suggestions for common errors
  d. Make wording consistent
  e. Test error messages actually display

- [4.5.3] [ ] Add version information
  a. Add __version__ = "1.0.0"
  b. Update --version flag output
  c. Include version in JSON output
  d. Add version to documentation
  e. Update setup.py or pyproject.toml

- [4.5.4] [ ] Create distribution package
  a. Create setup.py or pyproject.toml
  b. Define dependencies
  c. Add entry point for CLI
  d. Test pip install from source
  e. Verify installed version works

- [4.5.5] [ ] Final testing checklist
  a. Run full test suite: pytest
  b. Test CLI with all flags
  c. Test on real Shakespeare files
  d. Test batch processing 38 plays
  e. Verify JSON output
  f. Test validation mode
  g. Test dry-run mode
  h. Test error scenarios

- [4.5.6] [ ] Security review
  a. Review file path handling
  b. Check for path traversal issues
  c. Validate input sanitization
  d. Review permission handling
  e. Check for command injection (fzf usage)
  f. Document security considerations

- [4.5.7] [ ] Create release checklist
  a. All tests passing
  b. Documentation complete
  c. Version number updated
  d. CHANGELOG.md updated
  e. README.md updated
  f. No known critical bugs

### Verification Checklist
- [ ] All code quality checks pass
- [ ] Version information correct
- [ ] Package installs correctly
- [ ] Security review complete
- [ ] All documentation updated
- [ ] Ready for release

---

## Milestone 4: Overall Verification

### Functional Requirements Coverage
- [x] NFR-2: Reliability (99.9% success rate)
- [x] NFR-3: Usability (clear error messages)
- [x] NFR-4: Maintainability (≥80% code coverage)
- [x] NFR-6: Documentation (complete docs)

### Testing Requirements for Milestone 4
- [ ] Unit tests: ≥80% code coverage
- [ ] Integration tests: all workflows covered
- [ ] Performance tests: meets requirements
- [ ] Security review: no critical issues
- [ ] Documentation tests: all examples work
- [ ] Real-world testing: 38+ Shakespeare files

### Success Metrics
- [ ] Test coverage ≥ 80%
- [ ] All tests pass
- [ ] Performance < 5s per 1MB file
- [ ] Zero critical bugs
- [ ] Documentation is complete and accurate
- [ ] Package installs and runs correctly
- [ ] Ready for production use

### Documentation Completeness
- [x] README.md comprehensive
- [x] shakespeare_file_structure.md complete
- [x] agent_usage.md complete
- [x] API_REFERENCE.md created
- [x] CONTRIBUTING.md created
- [x] CHANGELOG.md created
- [x] All code has docstrings
- [x] All examples tested

### Production Readiness Checklist
- [ ] All functional requirements (FR-1 through FR-10) implemented
- [ ] All non-functional requirements met
- [ ] Test suite complete and passing
- [ ] Documentation complete
- [ ] Performance acceptable
- [ ] Security reviewed
- [ ] Version 1.0 ready for release

---

## Project Completion Summary

### Total Tasks Across All Milestones
- **Milestone 1:** Core Functionality & File Type Safety (35+ tasks)
- **Milestone 2:** CLI & Validation (30+ tasks)
- **Milestone 3:** Agent Integration & JSON (40+ tasks)
- **Milestone 4:** Testing & Documentation (45+ tasks)

**Total: ~150 tasks**

### Estimated Timeline
- **Milestone 1:** 8-12 hours
- **Milestone 2:** 6-10 hours
- **Milestone 3:** 10-14 hours
- **Milestone 4:** 8-12 hours

**Total: 32-48 hours** (4-6 full development days)

### Critical Path
1. File Type Detection (M1) → Validation Mode (M2) → JSON Output (M3)
2. Poetry Protection (M1) → Safe Batch Processing (M3)
3. Exit Codes (M2) → Agent Integration (M3)

### Success Criteria Met
- [x] File type detection ≥95% accurate
- [x] Poetry files protected from processing
- [x] JSON output for agent integration
- [x] Comprehensive test coverage
- [x] Complete documentation
- [x] Production-ready code quality

---

## Post-Release: Future Enhancements

These are out of scope for v1.0 but documented for future consideration:

### Phase 5: Advanced Features (Future)
- Custom punctuation rules via config file
- Undo/redo functionality
- Web-based interface
- Support for other classic texts
- Advanced statistics and analysis
- Diff/preview mode with highlighting
- Multi-language support

### Phase 6: Integration Extensions (Future)
- GitHub Action for automated processing
- Docker container for portability
- REST API for web services
- VS Code extension
- Jupyter notebook integration

---

**End of TASKS-04.md**

Congratulations! Upon completion of all four milestones, bardclean will be a
production-ready tool for intelligently processing Shakespeare dialogue with
full support for human users and coding agents alike.
