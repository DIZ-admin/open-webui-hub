# Pull Request

## 📋 Description

<!-- Provide a brief description of the changes in this PR -->

## 🔗 Related Issues

<!-- Link to any related issues -->
Fixes #(issue number)
Relates to #(issue number)

## 🎯 Type of Change

<!-- Mark the relevant option with an "x" -->

- [ ] 🐛 Bug fix (non-breaking change which fixes an issue)
- [ ] ✨ New feature (non-breaking change which adds functionality)
- [ ] 💥 Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] 📚 Documentation update
- [ ] 🔧 Configuration change
- [ ] 🧪 Test update
- [ ] 🔄 Refactoring (no functional changes)
- [ ] ⚡ Performance improvement
- [ ] 🔒 Security improvement

## 🧪 Testing

<!-- Describe the tests you ran to verify your changes -->

### Test Environment
- [ ] Local development environment
- [ ] Docker Compose setup
- [ ] CI/CD pipeline

### Test Cases
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] Performance testing (if applicable)
- [ ] Security testing (if applicable)

### Test Commands
```bash
# Commands used to test the changes
docker-compose -f compose.local.yml up -d
python tests/integration_testing.py
# Add other test commands here
```

## 📊 Performance Impact

<!-- If applicable, describe any performance implications -->

- [ ] No performance impact
- [ ] Performance improvement
- [ ] Potential performance regression (explain below)

## 🔒 Security Considerations

<!-- If applicable, describe any security implications -->

- [ ] No security impact
- [ ] Security improvement
- [ ] Potential security implications (explain below)

## 📸 Screenshots/Recordings

<!-- If applicable, add screenshots or recordings to help explain your changes -->

## 📝 Checklist

### Code Quality
- [ ] My code follows the project's style guidelines
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings

### Testing
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] I have tested the changes in a Docker environment

### Documentation
- [ ] I have updated the README.md if needed
- [ ] I have updated relevant documentation in the `docs/` directory
- [ ] I have added/updated comments in the code where necessary

### Dependencies
- [ ] I have not introduced any new dependencies without discussion
- [ ] If I added dependencies, I have updated the relevant requirements files
- [ ] I have verified that all dependencies are properly licensed

### Docker & Deployment
- [ ] Docker images build successfully
- [ ] Docker Compose configuration is valid
- [ ] Changes work in both development and production environments
- [ ] I have tested the deployment process

## 🔄 Migration Notes

<!-- If this PR requires any migration steps, document them here -->

- [ ] No migration required
- [ ] Database migration required
- [ ] Configuration changes required
- [ ] Manual steps required (document below)

### Manual Steps
```bash
# If manual steps are required, document them here
```

## 📚 Additional Notes

<!-- Add any additional notes, context, or considerations for reviewers -->

## 🏷️ Labels

<!-- Suggest appropriate labels for this PR -->
Suggested labels: `bug`, `enhancement`, `documentation`, `docker`, `ci/cd`, `security`, etc.

---

### For Reviewers

- [ ] Code review completed
- [ ] Testing verified
- [ ] Documentation reviewed
- [ ] Security implications considered
- [ ] Performance impact assessed
