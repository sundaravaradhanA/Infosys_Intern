import React from "react";
import { useNavigate } from "react-router-dom";
import bg from "../assets/login-bg.jpg";

function Register() {
  const navigate = useNavigate();

  return (
    <div
      className="min-h-screen flex items-center justify-center bg-cover bg-center"
      style={{ backgroundImage: `url(${bg})` }}
    >
      <div className="bg-white/90 backdrop-blur-md p-8 rounded-2xl shadow-lg w-96">
        <h2 className="text-3xl font-bold mb-8 text-center text-blue-600">
          Create Account
        </h2>

        <input
          type="text"
          placeholder="Full Name"
          className="w-full mb-4 p-3 border rounded-lg"
        />

        <input
          type="email"
          placeholder="Email"
          className="w-full mb-4 p-3 border rounded-lg"
        />

        <input
          type="password"
          placeholder="Password"
          className="w-full mb-4 p-3 border rounded-lg"
        />

        <input
          type="password"
          placeholder="Confirm Password"
          className="w-full mb-5 p-3 border rounded-lg"
        />

        <div className="flex justify-center">
          <button
            onClick={() => navigate("/")}
            className="px-10 py-3 text-lg font-semibold text-white
                       bg-gradient-to-r from-blue-500 to-blue-600
                       rounded-full shadow-lg
                       hover:from-blue-600 hover:to-blue-700
                       transition duration-300"
          >
            Register
          </button>
        </div>

        <p className="text-center text-sm mt-5">
          Already have an account?
          <button
            onClick={() => navigate("/")}
            className="ml-1 text-blue-600 font-semibold hover:underline"
          >
            Login
          </button>
        </p>
      </div>
    </div>
  );
}

export default Register;
