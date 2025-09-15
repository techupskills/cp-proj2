# Deployment Guide - Customer Support AI Agent

This guide covers deploying the AI Customer Support Agent to various platforms.

## Local Development

### Quick Start
```bash
# Install dependencies
pip install -r requirements.txt

# Start Ollama
ollama serve &
ollama pull llama3.2

# Run application
streamlit run streamlit_app.py
```

## Docker Deployment

### Build and Run
```bash
# Build image
docker build -t customer-support-ai .

# Run container
docker run -p 8501:8501 -p 11434:11434 customer-support-ai

# Or use docker-compose
docker-compose up
```

### Key Points:
- Container includes both Ollama and Streamlit
- Ports 8501 (Streamlit) and 11434 (Ollama) exposed
- Model downloaded on first startup (may take 5-10 minutes)

## Cloud Deployments

### Heroku
```bash
# Install Heroku CLI and login
heroku login

# Create app
heroku create your-app-name

# Deploy
git push heroku main
```

**Note**: Heroku has limitations with large models. Consider using smaller models like `llama3.2:1b`.

### AWS ECS
1. Build and push Docker image to ECR
2. Create ECS cluster
3. Register task definition (use `task-definition.json`)
4. Create ECS service

### Google Cloud App Engine
```bash
# Deploy using app.yaml
gcloud app deploy
```

### Kubernetes
```bash
# Apply manifests
kubectl apply -f k8s-deployment.yaml

# Check status
kubectl get pods
kubectl get services
```

## Monitoring

### Health Checks
- Health check endpoint: `/health_check.py`
- Monitors Ollama service and AI agent functionality
- Returns JSON status for automated monitoring

### Logs
- Streamlit logs: Application events and user interactions
- Ollama logs: Model loading and inference
- Container logs: System-level events

## Performance Considerations

### Resource Requirements:
- **Minimum**: 4GB RAM, 2 CPU cores
- **Recommended**: 8GB RAM, 4 CPU cores
- **Storage**: 5GB for llama3.2 model

### Scaling:
- **Horizontal**: Multiple container instances with load balancer
- **Vertical**: Increase container resources for better performance
- **Model Selection**: Use smaller models (llama3.2:1b) for faster responses

## Security

### Best Practices:
- Use environment variables for configuration
- Enable HTTPS in production
- Implement authentication for production deployments
- Regular security updates for base images

### Network Security:
- Restrict Ollama port (11434) to internal traffic only
- Use reverse proxy for SSL termination
- Implement rate limiting

## Troubleshooting

### Common Issues:

**Container won't start:**
- Check available memory (needs 4GB minimum)
- Verify Docker has sufficient resources allocated

**Model download fails:**
- Increase container startup timeout
- Check internet connectivity
- Try smaller model variant

**Slow responses:**
- Monitor CPU/memory usage
- Consider model optimization
- Implement response caching

**Connection errors:**
- Verify Ollama service is running
- Check port forwarding configuration
- Test with health check endpoint

## Production Checklist

- [ ] Environment variables configured
- [ ] Health checks implemented
- [ ] Monitoring and logging set up
- [ ] Backup and recovery procedures
- [ ] Security review completed
- [ ] Performance testing done
- [ ] Documentation updated

## Support

For deployment issues:
1. Check logs for error details
2. Run health check endpoint
3. Verify system requirements
4. Test with minimal configuration

For the full AI Enterprise Accelerator Training program, participants learn to deploy these systems in production environments with enterprise-grade security and monitoring.
