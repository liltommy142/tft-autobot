"""
CONTRIBUTING.md - Hướng dẫn đóng góp cho project
"""

# Contribution Guide

Cảm ơn bạn muốn đóng góp cho TFT Auto-bot! Dưới đây là hướng dẫn.

## 🛠️ Development Setup

```bash
# 1. Clone repo
git clone https://github.com/your-username/tft-autobot.git
cd tft-autobot

# 2. Create virtual environment
python -m venv .venv
.venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
pip install -r dev-requirements.txt

# 4. Run tests
pytest -v
```

## 📋 Code Style

- **Type hints**: Tất cả hàm phải có type hints đầy đủ
- **Docstrings**: Sử dụng format Google-style docstrings
- **Format**: Black (Run `black core_*.py cli_*.py`)
- **Lint**: Flake8 (Run `flake8 .`)
- **Imports**: isort (Run `isort .`)

### Ví dụ Code Style

```python
def recommend_items(
    gs: GameState, 
    target_comp: Optional[Dict[str, Any]]
) -> List[Dict[str, str]]:
    """Recommend items for target comp.
    
    Args:
        gs: Current game state
        target_comp: Target composition data
        
    Returns:
        List of item recommendations
        
    Raises:
        FileNotFoundError: If items.json not found
    """
    # Implementation...
    pass
```

## 🧪 Testing

- Viết unit tests cho mỗi hàm public
- Run `pytest` trước khi submit PR
- Aim for >80% code coverage

```bash
pytest --cov=core_models --cov=core_engine --cov=cli_main
```

## 🎯 Contribution Areas

### High Priority

1. **Improve Meta Logic**: Thêm sophisticated scoring algorithm
2. **Web UI**: Flask/Django frontend để nhập game state
3. **Real-time Match Tracking**: Stream live match data
4. **Advanced Econ**: Model-based economic decisions

### Medium Priority

1. **Discord Bot**: Bot command để get recommendations
2. **Mobile App**: React Native app
3. **Database**: SQLite/MongoDB for persistent logs
4. **Charts**: Visualization của winrate by comp

### Low Priority

1. **Localization**: Thêm language support
2. **Performance**: Optimize scoring algorithms
3. **Caching**: Cache meta data locally

## 📝 Commit Message Format

```
[Type] Short description

Long description (if needed)

Type: feat, fix, refactor, docs, test, perf, style
```

### Ví dụ:

```
[feat] Add unit star validation to UnitInstance

- Validates star level is 1-3
- Raises ValueError on invalid input
- Adds docstring with examples

Fixes #123
```

## 🔄 Pull Request Process

1. Fork repo
2. Create feature branch: `git checkout -b feature/description`
3. Make changes & add tests
4. Run format & lint:
   ```bash
   black .
   isort .
   flake8 .
   pytest
   ```
5. Commit with proper message
6. Push branch & create PR
7. Describe changes in PR body

## 🚀 Release Process

1. Update version in version file
2. Update CHANGELOG.md
3. Create git tag: `git tag v0.2.0`
4. Push: `git push --tags`
5. Create GitHub release with notes

## ❓ Questions?

- Open issue cho bugs/ideas
- Discussion tab cho general questions
- Email maintainer nếu cần

---

**Thank you for contributing! 🙏**
