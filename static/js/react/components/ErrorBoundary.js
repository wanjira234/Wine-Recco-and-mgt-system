import React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { 
      hasError: false,
      error: null,
      errorInfo: null 
    };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    this.setState({
      error: error,
      errorInfo: errorInfo
    });
    // You can log the error to an error reporting service
    console.error("Uncaught error:", error, errorInfo);
    
    // Optional: Send error to your error tracking service
    // if (typeof window.errorTrackingService !== 'undefined') {
    //   window.errorTrackingService.captureException(error, { extra: errorInfo });
    // }
  }
  
  handleReload = () => {
    window.location.reload();
  };
  
  handleGoHome = () => {
    window.location.href = '/';
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-4">
          <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-6 text-center">
            <div className="inline-flex items-center justify-center w-16 h-16 mb-6 bg-red-100 rounded-full text-red-600">
              <AlertTriangle className="h-8 w-8" />
            </div>
            
            <h1 className="text-2xl font-bold text-gray-900 mb-2">Something went wrong</h1>
            <p className="text-gray-600 mb-6">
              We're sorry, but an unexpected error has occurred. Our team has been notified.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <button
                onClick={this.handleReload}
                className="inline-flex items-center justify-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-wine-600 hover:bg-wine-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-wine-500"
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                Reload Page
              </button>
              <button
                onClick={this.handleGoHome}
                className="inline-flex items-center justify-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-wine-500"
              >
                Return to Home
              </button>
            </div>
            
            {this.props.showDetails && (
              <details className="mt-6 text-left bg-gray-50 p-4 rounded-md border border-gray-200">
                <summary className="text-sm font-medium text-gray-700 cursor-pointer">Error Details</summary>
                <div className="mt-2">
                  <p className="text-sm text-red-600 font-mono">
                    {this.state.error && this.state.error.toString()}
                  </p>
                  <pre className="mt-2 text-xs text-gray-600 overflow-auto p-2 bg-gray-100 rounded">
                    {this.state.errorInfo && this.state.errorInfo.componentStack}
                  </pre>
                </div>
              </details>
            )}
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;