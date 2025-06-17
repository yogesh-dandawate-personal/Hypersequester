# Hypersequester Deployment Guide

## 🚀 Quick Deploy to Netlify

### Option 1: One-Click Deploy (Recommended)

[![Deploy to Netlify](https://www.netlify.com/img/deploy/button.svg)](https://app.netlify.com/start/deploy?repository=https://github.com/Instoradmin/Hypersequester)

### Option 2: Manual Deployment

1. **Fork this repository** to your GitHub account

2. **Connect to Netlify**:
   - Go to [netlify.com](https://netlify.com)
   - Click "New site from Git"
   - Choose GitHub and select your forked repository
   - Branch: `Development`
   - Build command: `npm run build:netlify`
   - Publish directory: `build`

3. **Set Environment Variables** (optional):
   ```
   REACT_APP_API_URL=https://your-backend-api.com/api/v1
   REACT_APP_ENVIRONMENT=production
   NODE_VERSION=18
   ```

4. **Deploy**: Click "Deploy site"

## 🌐 Live Demo

- **Demo Site**: https://hypersequester.netlify.app
- **Features**: Full frontend functionality with sample data
- **Mode**: Automatic demo mode when backend is unavailable

## 📋 What's Included

### Frontend Application
- ✅ React.js 18 with modern hooks
- ✅ Ant Design UI components
- ✅ Interactive dashboard and data visualization
- ✅ Responsive design for all devices
- ✅ Progressive Web App (PWA) features

### Demo Mode
- ✅ Sample forest properties and assessments
- ✅ Realistic carbon estimation data
- ✅ Interactive charts and visualizations
- ✅ Full UI functionality without backend

### Performance Optimizations
- ✅ Code splitting and lazy loading
- ✅ Optimized bundle size
- ✅ CDN delivery via Netlify
- ✅ Automatic HTTPS and SSL

## 🔧 Local Development

```bash
# Clone the repository
git clone https://github.com/Instoradmin/Hypersequester.git
cd Hypersequester

# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm run build:netlify
```

## 📱 Browser Support

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)

## 🔗 Backend Integration

The frontend is designed to work with the Hypersequester backend API:

- **Development**: Local Flask server at `http://localhost:5000`
- **Production**: Configurable via `REACT_APP_API_URL`
- **Fallback**: Demo mode with sample data

## 📚 Documentation

- [Development Guide](docs/DEVELOPMENT_GUIDE.md)
- [Netlify Deployment](docs/NETLIFY_DEPLOYMENT.md)
- [API Documentation](docs/API_REFERENCE.md)
- [User Manual](docs/USER_MANUAL.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally
5. Submit a pull request

## 📞 Support

- **GitHub Issues**: Bug reports and feature requests
- **Documentation**: Comprehensive guides in `/docs`
- **Demo**: Try the live demo to see all features

---

**Built with ❤️ for forest carbon assessment**
