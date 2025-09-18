// import React, { useState } from 'react';
// import './style-signin.css';
// import 'material-design-iconic-font/dist/css/material-design-iconic-font.min.css';

// function Signin() {
//   const [signupMode, setSignupMode] = useState(false);

//   return (
//     <div className={signupMode ? 'signup-mode' : ''}>
//       <header>
//         <div className="logo">
//           <h1>
//             SugarFree
//             <span className="subtitle">AI Diabetes Screening</span>
//           </h1>
//         </div>
//       </header>

//       <main>
//         <div className="left-side">
//           <div className="login-form">
//             <h2>Welcome Back</h2>
//             <form>
//               <div className="form-group">
//                 <div className="form-icon">
//                   <i className="zmdi zmdi-email"></i>
//                 </div>
//                 <input type="email" name="email" id="email" required />
//                 <label htmlFor="email" className="floating-label">Email</label>
//               </div>
//               <div className="form-group">
//                 <div className="form-icon">
//                   <i className="zmdi zmdi-lock"></i>
//                 </div>
//                 <input type="password" name="pass" id="pass" required />
//                 <label htmlFor="pass" className="floating-label">Password</label>
//               </div>
//               <div className="options">
//                 <label><input type="checkbox" /> Remember me</label>
//                 <a href="#">Forgot Password?</a>
//               </div>
//               <button type="submit">Sign In</button>
//             </form>
//             <div className="signup-link">
//               <p>Don't have an account yet? <a href="#" onClick={(e) => { e.preventDefault(); setSignupMode(true); }}>Sign Up</a></p>
//             </div>
//             <a className="admin-link" href="#">Sign In as Admin</a>
//           </div>
//         </div>

//         <div className="right-side">
//           <div className="signup-form">
//             <h2>Create your account</h2>
//             <form>
//               <div className="form-group">
//                 <div className="form-icon">
//                   <i className="zmdi zmdi-account"></i>
//                 </div>
//                 <input type="text" name="username" id="username" required />
//                 <label htmlFor="username" className="floating-label">Username</label>
//               </div>
//               <div className="form-group">
//                 <div className="form-icon">
//                   <i className="zmdi zmdi-lock"></i>
//                 </div>
//                 <input type="password" name="password" id="password" required />
//                 <label htmlFor="password" className="floating-label">Password</label>
//               </div>
//               <div className="form-group">
//                 <div className="form-icon">
//                   <i className="zmdi zmdi-email"></i>
//                 </div>
//                 <input type="email" name="email" id="email-signup" required />
//                 <label htmlFor="email-signup" className="floating-label">Email</label>
//               </div>
//               <button type="submit">Sign Up</button>
//             </form>
//             <div className="signin-link">
//               <p>Already have an account? <a href="#" onClick={(e) => { e.preventDefault(); setSignupMode(false); }}>Sign In</a></p>
//             </div>
//           </div>
//         </div>

//         <div className="overlay"></div>
//       </main>
//     </div>
//   );
// }

// export default Signin;


import React, { useState } from 'react';
import './Sign.css';
import signinbg from './images/signinbg.jpg';
import signupbg from './images/signupbg.jpg';

const Sign = () => {
  const [isSignIn, setIsSignIn] = useState(true);

  const handleToggle = () => {
    setIsSignIn(!isSignIn);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    alert(isSignIn ? 'Signed In!' : 'Signed Up!');
    // TODO: redirect to dashboard or save to backend
  };

  return (
    <div className="container-auth">
      <div
        className="auth-panel"
        style={{
          backgroundImage: `url(${isSignIn ? signinbg : signupbg})`,
        }}
      >
        <div className="form-box">
          <h1 className="logo">SugarFree</h1>
          <p className="subtitle">AI Diabetes Screening</p>


          <h2 className="form-title">{isSignIn ? 'Welcome Back' : 'Create your account'}</h2>

          <form className="auth-form" onSubmit={handleSubmit}>
            {!isSignIn && (
              <input
                type="text"
                name="username"
                placeholder="Username"
                required
              />
            )}
            <input
              type="email"
              name="email"
              placeholder="Email"
              required
            />
            <input
              type="password"
              name="password"
              placeholder="Password"
              required
            />
            <button type="submit">{isSignIn ? 'Sign In' : 'Sign Up'}</button>
          </form>

          <div className="switch-mode">
            <span>{isSignIn ? "Don't have an account?" : 'Already have an account?'}</span>
            <button onClick={handleToggle}>
              {isSignIn ? 'Sign Up' : 'Sign In'}
            </button>
          </div>

          {isSignIn && <p className="admin-link">Sign in as Admin</p>}
        </div>
      </div>
    </div>
  );
};

export default Sign;