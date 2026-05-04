# Software Engineering - Practice work

Subject: *A simple Python 'Hay Day'-like farming game*

## Links

- [Specification](https://github.com/Septicuss/hy-ot-harjoitustyo/blob/main/docs/specification.md)
- [Time Tracking](https://github.com/Septicuss/hy-ot-harjoitustyo/blob/main/docs/timetracking.md)
- [Changelog](https://github.com/Septicuss/hy-ot-harjoitustyo/blob/main/docs/changelog.md)
- [Architecture](https://github.com/Septicuss/hy-ot-harjoitustyo/blob/main/docs/architecture.md)
- [Usage Guide](https://github.com/Septicuss/hy-ot-harjoitustyo/blob/main/docs/guide.md)

**Releases**
- [Release Week 5](https://github.com/Septicuss/hy-ot-harjoitustyo/releases/tag/viikko5)
- [Release Week 6](https://github.com/Septicuss/hy-ot-harjoitustyo/releases/tag/viikko6)

## Installation

(More detailed usage guide in [Usage Guide](https://github.com/Septicuss/hy-ot-harjoitustyo/blob/main/docs/guide.md))

1. Install Poetry dependencies with

```
poetry install
```

2. Start the application
```
poetry run invoke start
```

## Commands

### Start the application
```
poetry run invoke start
```

### Testing
```
poetry run invoke test
```

### Linter
```
poetry run invoke lint
```

### Coverage report
```
poetry run invoke coverage-report
```
