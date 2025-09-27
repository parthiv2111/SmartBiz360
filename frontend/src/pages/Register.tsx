import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { Eye, EyeOff, Building2 } from 'lucide-react';
import { useApp } from '../contexts/AppContext';
import { authAPI } from '../services/api';

const Register: React.FC = () => {
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    confirmPassword: '',
    company: '',
    agreeToTerms: false,
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [apiError, setApiError] = useState<string | null>(null);

  const { login, addNotification } = useApp();
  const navigate = useNavigate();
  const location = useLocation();
  
  const from = (location.state as any)?.from?.pathname || '/';

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.firstName) newErrors.firstName = 'First name is required';
    if (!formData.lastName) newErrors.lastName = 'Last name is required';
    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email is invalid';
    }
    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    }
    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }
    if (!formData.company) newErrors.company = 'Company name is required';
    if (!formData.agreeToTerms) newErrors.agreeToTerms = 'You must agree to the terms';

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setApiError(null);
    if (!validateForm()) return;

    setIsLoading(true);
    
    try {
      const response = await authAPI.register({
        first_name: formData.firstName,
        last_name: formData.lastName,
        email: formData.email,
        password: formData.password,
        company: formData.company,
      });
      
      if (response.success) {
        const { user, access_token, refresh_token } = response.data;
        login(user, { access_token, refresh_token });
        addNotification('success', 'Registration successful! Welcome.');
        navigate(from, { replace: true });
      }
    } catch (error: any) {
      setApiError(error.message || 'Registration failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({ 
      ...prev, 
      [name]: type === 'checkbox' ? checked : value 
    }));
    
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="flex justify-center">
          <Building2 className="w-12 h-12 text-primary-600" />
        </div>
        <h2 className="mt-6 text-center text-3xl font-bold text-gray-900">
          Create your account
        </h2>
        <p className="mt-2 text-center text-sm text-gray-600">
          Or{' '}
          <Link to="/login" className="font-medium text-primary-600 hover:text-primary-500">
            sign in to your existing account
          </Link>
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="card py-8 px-4 sm:px-10">
          {apiError && (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-600 text-sm">{apiError}</p>
            </div>
          )}
          <form className="space-y-4" onSubmit={handleSubmit}>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <label htmlFor="firstName">First name</label>
                <input id="firstName" name="firstName" type="text" required value={formData.firstName} onChange={handleChange} className={`input-field ${errors.firstName ? 'border-error-300' : ''}`} />
                {errors.firstName && <p className="mt-1 text-sm text-error-600">{errors.firstName}</p>}
              </div>
              <div>
                <label htmlFor="lastName">Last name</label>
                <input id="lastName" name="lastName" type="text" required value={formData.lastName} onChange={handleChange} className={`input-field ${errors.lastName ? 'border-error-300' : ''}`} />
                {errors.lastName && <p className="mt-1 text-sm text-error-600">{errors.lastName}</p>}
              </div>
            </div>

            <div>
              <label htmlFor="email">Email address</label>
              <input id="email" name="email" type="email" required value={formData.email} onChange={handleChange} className={`input-field ${errors.email ? 'border-error-300' : ''}`} />
              {errors.email && <p className="mt-1 text-sm text-error-600">{errors.email}</p>}
            </div>

            <div>
              <label htmlFor="company">Company name</label>
              <input id="company" name="company" type="text" required value={formData.company} onChange={handleChange} className={`input-field ${errors.company ? 'border-error-300' : ''}`} />
              {errors.company && <p className="mt-1 text-sm text-error-600">{errors.company}</p>}
            </div>

            <div>
              <label htmlFor="password">Password</label>
              <div className="relative">
                <input id="password" name="password" type={showPassword ? 'text' : 'password'} required value={formData.password} onChange={handleChange} className={`input-field pr-10 ${errors.password ? 'border-error-300' : ''}`} />
                <button type="button" className="absolute inset-y-0 right-0 pr-3 flex items-center" onClick={() => setShowPassword(!showPassword)}>
                  {showPassword ? <EyeOff className="h-5 w-5 text-gray-400" /> : <Eye className="h-5 w-5 text-gray-400" />}
                </button>
              </div>
              {errors.password && <p className="mt-1 text-sm text-error-600">{errors.password}</p>}
            </div>

            <div>
              <label htmlFor="confirmPassword">Confirm password</label>
              <div className="relative">
                <input id="confirmPassword" name="confirmPassword" type={showConfirmPassword ? 'text' : 'password'} required value={formData.confirmPassword} onChange={handleChange} className={`input-field pr-10 ${errors.confirmPassword ? 'border-error-300' : ''}`} />
                <button type="button" className="absolute inset-y-0 right-0 pr-3 flex items-center" onClick={() => setShowConfirmPassword(!showConfirmPassword)}>
                  {showConfirmPassword ? <EyeOff className="h-5 w-5 text-gray-400" /> : <Eye className="h-5 w-5 text-gray-400" />}
                </button>
              </div>
              {errors.confirmPassword && <p className="mt-1 text-sm text-error-600">{errors.confirmPassword}</p>}
            </div>

            <div className="flex items-start">
              <input id="agreeToTerms" name="agreeToTerms" type="checkbox" checked={formData.agreeToTerms} onChange={handleChange} className="h-4 w-4 text-primary-600 rounded mt-1" />
              <label htmlFor="agreeToTerms" className="ml-2 block text-sm text-gray-900">
                I agree to the{' '}
                <Link to="/terms" target="_blank" className="text-primary-600 hover:text-primary-500">
                  Terms and Conditions
                </Link>
              </label>
            </div>
            {errors.agreeToTerms && <p className="text-sm text-error-600">{errors.agreeToTerms}</p>}

            <div>
              <button type="submit" disabled={isLoading} className="btn-primary w-full flex justify-center py-2 px-4 mt-2">
                {isLoading ? <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div> : 'Create account'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Register;