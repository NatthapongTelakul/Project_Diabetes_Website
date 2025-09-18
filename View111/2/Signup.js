import React from 'react';
import './style-sign.css';
import 'material-design-iconic-font/dist/css/material-design-iconic-font.min.css';
import { useNavigate } from 'react-router-dom';

function Signup() {
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    // TODO: ส่งข้อมูลไป backend
    alert('Sign up submitted!');
  };

  return (
    <div className="right-side">
      <div className="signup-form">
        <h2>Create your account</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <div className="form-icon">
              <i className="zmdi zmdi-account"></i>
            </div>
            <input type="text" name="username" id="username" required />
            <label htmlFor="username" className="floating-label">Username</label>
          </div>
          <div className="form-group">
            <div className="form-icon">
              <i className="zmdi zmdi-lock"></i>
            </div>
            <input type="password" name="password" id="password" required />
            <label htmlFor="password" className="floating-label">Password</label>
          </div>
          <div className="form-group">
            <div className="form-icon">
              <i className="zmdi zmdi-email"></i>
            </div>
            <input type="email" name="email" id="email-signup" required />
            <label htmlFor="email-signup" className="floating-label">Email</label>
          </div>
          <button type="submit">Sign Up</button>
        </form>
        <div className="signin-link">
          <p>Already have an account? <a href="#" onClick={(e) => { e.preventDefault(); navigate('/signin'); }}>Sign In</a></p>
        </div>
      </div>
    </div>
  );
}

export default Signup
