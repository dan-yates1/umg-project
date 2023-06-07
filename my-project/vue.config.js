module.exports = {
  // Base URL for assets in production
  publicPath: process.env.NODE_ENV === 'production' ? '' : '/',

  // Output directory for built files
  outputDir: 'dist',

  // Enable or disable source maps
  productionSourceMap: false,

  // Configure dev server options
  devServer: {
    port: 8080,
    open: true,
    // Additional dev server configurations
  },

  // Other configuration options
  // ...

  // CSS related options
  css: {
    // Enable CSS source maps
    sourceMap: true,

    // Additional CSS related options
  },

  // Configure webpack
  configureWebpack: {
    // Additional webpack configurations
  },

  // Customize the webpack-dev-server behavior
  chainWebpack: (config) => {
    // Additional webpack-dev-server configurations
  },
};
