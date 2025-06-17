# Netlify Deployment Guide - Hypersequester

This guide provides step-by-step instructions for deploying the Hypersequester frontend to Netlify.

## Overview

The Hypersequester application is deployed as a static React application on Netlify with the following features:
- **Demo Mode**: Fully functional frontend with sample data
- **API Integration**: Ready to connect to backend when available
- **Progressive Enhancement**: Graceful fallback to demo mode if API is unavailable
- **Optimized Build**: Production-ready with performance optimizations

## Prerequisites

- GitHub account with access to the Hypersequester repository
- Netlify account (free tier is sufficient)
- Node.js 18+ for local testing (optional)

## Deployment Methods

### Method 1: Automatic Deployment from GitHub (Recommended)

#### 1. Connect Repository to Netlify

1. **Login to Netlify**
   - Go to [netlify.com](https://netlify.com)
   - Sign in with your GitHub account

2. **Create New Site**
   - Click "New site from Git"
   - Choose "GitHub" as your Git provider
   - Select the `Hypersequester` repository
   - Choose the `Development` branch

3. **Configure Build Settings**
   ```
   Branch to deploy: Development
   Build command: npm run build:netlify
   Publish directory: build
   ```

4. **Environment Variables**
   Add these environment variables in Netlify dashboard:
   ```
   REACT_APP_API_URL=https://hypersequester-api.herokuapp.com/api/v1
   REACT_APP_ENVIRONMENT=production
   GENERATE_SOURCEMAP=false
   NODE_VERSION=18
   ```

5. **Deploy Site**
   - Click "Deploy site"
   - Netlify will automatically build and deploy your site
   - You'll get a random URL like `https://amazing-name-123456.netlify.app`

#### 2. Custom Domain (Optional)

1. **Add Custom Domain**
   - Go to Site settings > Domain management
   - Click "Add custom domain"
   - Enter your domain (e.g., `hypersequester.com`)

2. **Configure DNS**
   - Point your domain's DNS to Netlify's servers
   - Netlify will provide specific instructions

3. **Enable HTTPS**
   - Netlify automatically provides SSL certificates
   - HTTPS will be enabled within a few minutes

### Method 2: Manual Deployment

#### 1. Build Locally

```bash
# Clone the repository
git clone https://github.com/yogesh-dandawate-personal/Hypersequester.git
cd Hypersequester

# Install dependencies
npm install

# Build for production
npm run build:netlify
```

#### 2. Deploy to Netlify

1. **Drag and Drop**
   - Go to [netlify.com](https://netlify.com)
   - Drag the `build` folder to the deployment area

2. **Netlify CLI** (Alternative)
   ```bash
   # Install Netlify CLI
   npm install -g netlify-cli

   # Login to Netlify
   netlify login

   # Deploy
   netlify deploy --prod --dir=build
   ```

## Configuration Files

### netlify.toml

The `netlify.toml` file in the root directory contains:

```toml
[build]
  command = "npm run build:netlify"
  publish = "build"
  base = "."

[build.environment]
  NODE_VERSION = "18"
  REACT_APP_API_URL = "https://hypersequester-api.herokuapp.com/api/v1"
  REACT_APP_ENVIRONMENT = "production"
  GENERATE_SOURCEMAP = "false"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

### Build Script

The `build:netlify` script in `package.json`:

```json
{
  "scripts": {
    "build:netlify": "REACT_APP_API_URL=https://hypersequester-api.herokuapp.com/api/v1 npm run build"
  }
}
```

## Demo Mode Features

### Automatic Demo Mode

The application automatically enables demo mode when:
- Deployed on Netlify (hostname contains `netlify.app`)
- URL parameter `?demo=true` is present
- Backend API is not available

### Demo Data

Demo mode includes:
- **Sample Properties**: 3 forest properties with realistic data
- **Assessment History**: Various assessment states (completed, processing, pending)
- **Carbon Results**: Realistic carbon pool estimations
- **Interactive Features**: All UI components fully functional
- **Species Data**: Forest species distribution charts

### Demo Mode Indicator

A prominent banner shows when demo mode is active with options to:
- Try connecting to live API
- View source code on GitHub
- Understand demo limitations

## Performance Optimizations

### Build Optimizations

- **Code Splitting**: Automatic route-based code splitting
- **Tree Shaking**: Unused code elimination
- **Minification**: JavaScript and CSS minification
- **Source Maps**: Disabled in production for smaller builds

### Caching Strategy

```toml
[[headers]]
  for = "/static/*"
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"
```

### Bundle Analysis

```bash
# Analyze bundle size
npm run analyze
```

## Security Configuration

### Content Security Policy

```toml
[[headers]]
  for = "/*"
  [headers.values]
    Content-Security-Policy = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' https://hypersequester-api.herokuapp.com https://api.mapbox.com;"
```

### Security Headers

- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `X-Content-Type-Options: nosniff`
- `Referrer-Policy: strict-origin-when-cross-origin`

## Monitoring and Analytics

### Netlify Analytics

Enable Netlify Analytics for:
- Page views and unique visitors
- Top pages and referrers
- Bandwidth usage
- Performance metrics

### Error Monitoring

Consider integrating:
- **Sentry**: Error tracking and performance monitoring
- **LogRocket**: Session replay and debugging
- **Google Analytics**: User behavior analytics

## Troubleshooting

### Common Issues

#### 1. Build Failures

```bash
# Check build logs in Netlify dashboard
# Common fixes:
npm install  # Update dependencies
npm run build:netlify  # Test build locally
```

#### 2. Routing Issues

- Ensure `netlify.toml` has the redirect rule for React Router
- Check that all routes are defined in `App.js`

#### 3. API Connection Issues

- Verify `REACT_APP_API_URL` environment variable
- Check CORS configuration on backend
- Demo mode should activate automatically if API is unavailable

#### 4. Performance Issues

```bash
# Analyze bundle size
npm run analyze

# Check for large dependencies
npm ls --depth=0
```

### Debug Mode

Enable debug mode by adding `?debug=true` to URL:
- Shows API endpoints being called
- Displays demo mode status
- Logs performance metrics

## Continuous Deployment

### Automatic Deployments

Netlify automatically deploys when:
- Code is pushed to the `Development` branch
- Pull requests are merged
- Manual deploy is triggered

### Deploy Previews

- Every pull request gets a preview URL
- Test changes before merging
- Share previews with stakeholders

### Branch Deploys

Configure different branches for different environments:
- `main` → Production site
- `Development` → Staging site
- Feature branches → Preview deploys

## Custom Domains and SSL

### Domain Configuration

1. **Add Domain in Netlify**
   - Site settings → Domain management
   - Add custom domain

2. **DNS Configuration**
   ```
   Type: CNAME
   Name: www
   Value: your-site-name.netlify.app

   Type: A
   Name: @
   Value: 75.2.60.5
   ```

3. **SSL Certificate**
   - Automatically provisioned by Netlify
   - Includes www and apex domain
   - Auto-renewal enabled

## Environment Variables

### Required Variables

```bash
REACT_APP_API_URL=https://your-api-domain.com/api/v1
REACT_APP_ENVIRONMENT=production
NODE_VERSION=18
GENERATE_SOURCEMAP=false
```

### Optional Variables

```bash
REACT_APP_DEMO_MODE=true  # Force demo mode
REACT_APP_DEBUG=false     # Enable debug logging
REACT_APP_ANALYTICS_ID=   # Google Analytics ID
```

## Backup and Recovery

### Site Backup

- Netlify automatically backs up your site
- Deploy history available for rollbacks
- Download site files from dashboard

### Rollback Procedure

1. Go to Deploys tab in Netlify dashboard
2. Find previous successful deploy
3. Click "Publish deploy" to rollback

## Support and Resources

### Netlify Documentation

- [Netlify Docs](https://docs.netlify.com/)
- [Build Configuration](https://docs.netlify.com/configure-builds/)
- [Custom Domains](https://docs.netlify.com/domains-https/)

### Hypersequester Resources

- [GitHub Repository](https://github.com/Instoradmin/Hypersequester)
- [Development Guide](DEVELOPMENT_GUIDE.md)
- [API Documentation](API_REFERENCE.md)

### Getting Help

1. **Check Netlify Build Logs**
   - Detailed error messages
   - Build step information

2. **Test Locally**
   ```bash
   npm run build:netlify
   npm run serve
   ```

3. **Contact Support**
   - Create GitHub issue
   - Include build logs and error messages

---

**Last Updated**: June 17, 2024
**Netlify Site**: https://hypersequester.netlify.app
**Status**: Ready for deployment
