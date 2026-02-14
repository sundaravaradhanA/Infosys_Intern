import React from "react";
import { useNavigate, Routes, Route, NavLink } from "react-router-dom";
import Accounts from "./Accounts";
import Transactions from "./Transactions";

function Dashboard() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex flex-col">
      
      {/* Header */}
      <header className="bg-blue-600 text-white flex justify-between items-center px-6 py-4">
        <h1 className="text-xl font-bold">My Banking App</h1>
        <button
          onClick={() => {
            localStorage.removeItem("auth");
            navigate("/");
          }}
          className="bg-white text-blue-600 px-4 py-2 rounded-lg font-semibold"
        >
          Logout
        </button>
      </header>

      <div className="flex flex-1">

        {/* Sidebar */}
        <aside className="w-64 bg-gray-100 p-6">
          <ul className="space-y-4">
            <li>
              <NavLink
                to="accounts"
                className={({ isActive }) =>
                  isActive ? "text-blue-600 font-bold" : "text-gray-700"
                }
              >
                Accounts
              </NavLink>
            </li>

            <li>
              <NavLink
                to="transactions"
                className={({ isActive }) =>
                  isActive ? "text-blue-600 font-bold" : "text-gray-700"
                }
              >
                Transactions
              </NavLink>
            </li>
          </ul>
        </aside>

        {/* Content */}
        <main className="flex-1 p-8 bg-gray-50">
          <Routes>
            <Route path="accounts" element={<Accounts />} />
            <Route path="transactions" element={<Transactions />} />
          </Routes>
        </main>

      </div>
    </div>
  );
}

export default Dashboard;
