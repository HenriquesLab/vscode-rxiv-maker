# ⚠️ DEPRECATED: Experimental Cairo Image

**This directory is deprecated as of rxiv-maker v1.8+**

## Migration Complete

The experimental Cairo features from this directory have been successfully merged into the base Docker image (`henriqueslab/rxiv-maker-base:latest`). The base image now provides all the Cairo enhancements that were previously available only in the experimental variant.

## What Changed

- **Base Image**: Now Cairo-only with enhanced SVG processing
- **Browser Dependencies**: Removed Chrome/Chromium from base image
- **Cross-Platform**: Native ARM64 and AMD64 support
- **Performance**: Improved performance with smaller image size

## Migration Guide

### Old Usage (Deprecated)
```bash
# DON'T USE - Experimental image no longer needed
RXIV_DOCKER_VARIANT=experimental-cairo rxiv pdf --engine docker
make pdf RXIV_ENGINE=DOCKER RXIV_DOCKER_VARIANT=experimental-cairo
```

### New Usage (Recommended)
```bash
# Use the enhanced base image directly
rxiv pdf --engine docker
make pdf RXIV_ENGINE=DOCKER
```

## Timeline

- **v1.7 and earlier**: Experimental Cairo image provided enhanced SVG processing
- **v1.8+**: All Cairo features merged into base image
- **Future**: This experimental directory will be removed in a future release

## Docker Images

| Image | Status | Recommendation |
|-------|--------|----------------|
| `henriqueslab/rxiv-maker-base:latest` | ✅ **Active** - Cairo-only | **Use this** |
| `henriqueslab/rxiv-maker-experimental:latest-cairo` | ⚠️ **Deprecated** | Migrate to base image |

## Need Help?

If you were using the experimental Cairo image and need help migrating, please:

1. **Update your scripts** to use the base image only
2. **Remove RXIV_DOCKER_VARIANT** environment variable references  
3. **Test your builds** with the new base image
4. **Report issues** if you encounter any problems during migration

The base image now provides all the Cairo functionality that was previously experimental.