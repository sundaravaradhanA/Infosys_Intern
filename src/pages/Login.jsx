import React from "react";
import { useNavigate } from "react-router-dom";
import bg from "../assets/login-bg.jpg";

function Login() {
  const navigate = useNavigate();

  return (
    <div
      className="min-h-screen flex items-center justify-center bg-cover bg-center"
      style={{ backgroundImage: `url(${bg})` }}
    >
      <div className="bg-white/90 backdrop-blur-md p-8 rounded-2xl shadow-lg w-96">
        <h1 className="text-6xl text-red-600 font-black text-center">
          Banking Login
        </h1>  
       /* <h2 className="text-3xl font-bold mb-8 text-center text-blue-600">
          Banking Login
        </h2> */

        <input
          type="email"
          placeholder="Enter Your Email"
          className="w-full mb-4 p-3 border rounded-lg"
        />

        <input
          type="password"
          placeholder="Enter Your Password"
          className="w-full mb-5 p-3 border rounded-lg"
        />

        <div className="flex justify-center">
          <button
            onClick={() => {
              localStorage.setItem("auth", "true");
              navigate("/dashboard/accounts");
            }}
            className="mt-5 px-10 py-3 text-lg font-semibold text-white
                       bg-gradient-to-r from-blue-500 to-blue-600
                       rounded-full shadow-lg
                       hover:from-blue-600 hover:to-blue-700
                       transition duration-300"
          >
            Login
          </button>
        </div>

        <p className="text-center text-sm mt-5">
          Don’t have an account?
          <button
            onClick={() => navigate("/register")}
            className="ml-1 text-blue-600 font-semibold hover:underline"
          >
            Register
          </button>
        </p>
      </div>
    </div>
  );
}

export default Login;
