
### Docker Issues

**Problem**: Containers won't start
```bash
# Check Docker is running
docker info

# Check logs
docker-compose logs

# Restart Docker Desktop
# Windows: Right-click Docker icon → Restart
# macOS: Click Docker icon → Restart
# Linux: sudo systemctl restart docker
```

**Problem**: Port already in use
```bash
# Find process using port (example: 5432)
# Windows:
netstat -ano | findstr :5432

# macOS/Linux:
lsof -i :5432

# Kill process or change port in docker-compose.yml
```

### Python Issues

**Problem**: `python` command not found
```bash
# Try python3
python3 --version

# Or create alias
# Windows PowerShell: Set-Alias python python3
# macOS/Linux: alias python=python3
```

**Problem**: Virtual environment activation fails
```bash
# Windows: Enable script execution
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then retry activation
```

### Git Issues

**Problem**: Permission denied (publickey)
```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your.email@example.com"

# Add to GitHub: Settings → SSH and GPG keys → New SSH key
# Copy public key:
cat ~/.ssh/id_ed25519.pub
```

---

## 9. NEXT STEPS

✅ **Phase 1 Complete!**

You now have:
- Professional GitHub repository
- Local development environment
- IBM Cloud environments (provisioned or in progress)
- CI/CD pipeline

**Next**: [PHASE_2_SENSOR_SIMULATOR.md](PHASE_2_SENSOR_SIMULATOR.md)

In Phase 2, you'll build the sensor simulator that generates realistic geothermal turbine data and publishes it to Watson IoT Platform.

---

## 📚 ADDITIONAL RESOURCES

- [Docker Documentation](https://docs.docker.com/)
- [Git Branching Strategy](https://nvie.com/posts/a-successful-git-branching-model/)
- [Python Virtual Environments](https://docs.python.org/3/tutorial/venv.html)
- [GitHub Actions](https://docs.github.com/en/actions)
- [IBM TechZone](https://techzone.ibm.com/collection/tech-zone-certified-base-images)

---

**Questions or issues? Document them and we'll address them together!**