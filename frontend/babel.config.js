module.exports = {
    presets: [
        ['@babel/preset-env', {
            targets: {
                browsers: ['last 2 versions', 'not dead']
            }
        }],
        ['@babel/preset-react', {
            runtime: 'automatic',
            development: process.env.NODE_ENV === 'development'
        }]
    ],
    plugins: [
        '@babel/plugin-transform-runtime',
        '@babel/plugin-proposal-class-properties',
        '@babel/plugin-proposal-object-rest-spread'
    ]
};