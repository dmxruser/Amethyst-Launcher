# The Roadmap

## Alpha

### Phase 1: Foundation (v0.1a)
- [x] Basic instance detection (Steam installations)
- [x] Basic instance detection (Local/Minecraft-style folders)
- [x] Launch instances via Steam
- [x] Geode mod detection
- [ ] Basic save management (swap to instance folder)
- [ ] Platform detection and path configuration

### Phase 2: Instance Management (v0.2a)
- [ ] Instance import/export functionality
- [ ] Instance backup system
- [ ] Instance renaming
- [ ] Custom instance icons/thumbnails
- [ ] Instance sorting and filtering
- [ ] Duplicate detection

### Phase 3: Save Management (v0.3a)
- [ ] Save profile system (multiple save slots per instance)
- [ ] Save export/import
- [ ] Auto-backup before launch
- [ ] Save versioning/history
- [ ] Cloud save support (via Steam Cloud)
- [ ] Manual save folder selection

### Phase 4: Geode Integration (v0.4a)
- [ ] Geode mod browser (fetch from Geode API if available)
- [ ] Mod install/uninstall from launcher
- [ ] Mod enable/disable toggle
- [ ] Mod dependency resolution
- [ ] Mod update checking
- [ ] Profile management improvements

## Beta

### Phase 5: Version Management (v0.5b)
- [ ] Version list display (from Steam depots)
- [ ] Version download improvements (more reliable than Steam console)
- [ ] Version rollback capability
- [ ] Version comparison
- [ ] Offline version support (manual folder import)

### Phase 6: Settings & Customization (v0.6b)
- [ ] Per-instance settings
- [ ] Launch arguments support
- [ ] Custom Steam launch options
- [ ] Theme support (dark/light)
- [ ] Language support (i18n)
- [ ] Portable mode option

### Phase 7: Data & Sync (v0.7b)
- [ ] Configuration sync between devices
- [ ] Instance data sync
- [ ] Settings import/export
- [ ] Account system (optional cloud features)

## v1.0 Release

### Phase 8: Polish (v1.0)
- [ ] Full automated testing
- [ ] Comprehensive error handling
- [ ] Performance optimization
- [ ] Final UI polish
- [ ] Documentation
- [ ] Stable release builds for Windows/Linux

---

## Technical Goals

### Core Principles
1. **Steam-first** - Always use Steam for launching and ownership to "not break shit"
2. **Non-destructive** - Never modify original game files without backup
3. **Portable** - Easy to move instances between machines
4. **Safe** - Always verify ownership before allowing actions

### Architecture Goals
- Modular design (separate managers for launch, geode, config, etc.)
- Cross-platform support (Windows, Linux)
- Plugin-ready for future extensibility
- Minimal dependencies

### Known Limitations (Will Not Add)
- Piracy/DRM bypass features
- Unofficial version sources
- Features that circumvent Steam verification

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to help implement this roadmap.