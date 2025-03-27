const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');

module.exports = {
    entry: './src/index.jsx',
    output: {
        path: path.resolve(__dirname, '../static/js'),
        filename: 'bundle.js',
        publicPath: '/static/js/'
    },
    module: {
        rules: [
            {
                test: /\.(js|jsx)$/,
                exclude: /node_modules/,
                use: {
                    loader: 'babel-loader',
                    options: {
                        presets: ['@babel/preset-react', '@babel/preset-env']
                    }
                }
            },
            {
                test: /\.css$/,
                use: [MiniCssExtractPlugin.loader, 'css-loader', 'postcss-loader']
            },
            {
                test: /\.(png|jpg|gif|svg|ico)$/,
                type: 'asset',
                parser: {
                    dataUrlCondition: {
                        maxSize: 10 * 1024 // 10kb
                    }
                },
                generator: {
                    filename: 'images/[name].[hash][ext]'
                }
            }
        ]
    },
    plugins: [
        new HtmlWebpackPlugin({
            template: './public/index.html',
            favicon: './public/favicon.ico'
        }),
        new MiniCssExtractPlugin({
            filename: '../css/styles.css'
        })
    ],
    resolve: {
        extensions: ['.js', '.jsx'],
        alias: {
            '@components': path.resolve(__dirname, 'src/components'),
            '@pages': path.resolve(__dirname, 'src/pages'),
            '@context': path.resolve(__dirname, 'src/context'),
            '@styles': path.resolve(__dirname, 'src/styles'),
            '@utils': path.resolve(__dirname, 'src/utils')
        }
    },
    optimization: {
        moduleIds: 'deterministic',
        runtimeChunk: 'single',
        splitChunks: {
            cacheGroups: {
                vendor: {
                    test: /[\\/]node_modules[\\/]/,
                    name: 'vendors',
                    chunks: 'all'
                }
            }
        }
    },
    devServer: {
        historyApiFallback: true,
        hot: true,
        port: 3000,
        proxy: {
            '/api': 'http://localhost:5000'
        }
    }
};