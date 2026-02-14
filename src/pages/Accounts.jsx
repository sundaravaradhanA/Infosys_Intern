import React from "react";
function Accounts() {
  const accounts = [
    { id: 1, bank: "HDFC Bank", type: "Savings", balance: "₹25,000" },
    { id: 2, bank: "SBI Bank", type: "Credit", balance: "₹10,000" },
    { id: 3, bank: "ICICI Bank", type: "Current", balance: "₹40,000" },
  ];

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Accounts</h2>

      <div className="bg-white shadow rounded-lg p-6">
        <table className="w-full">
          <thead>
            <tr className="text-left border-b">
              <th className="pb-2">Bank</th>
              <th className="pb-2">Type</th>
              <th className="pb-2">Balance</th>
            </tr>
          </thead>
          <tbody>
            {accounts.map((acc) => (
              <tr key={acc.id} className="border-b">
                <td className="py-3">{acc.bank}</td>
                <td>{acc.type}</td>
                <td className="font-semibold">{acc.balance}</td>
              </tr>
            ))}
          </tbody>
        </table>

        <button className="mt-6 bg-blue-600 text-white px-4 py-2 rounded-lg">
          + Add Account
        </button>
      </div>
    </div>
  );
}

export default Accounts;
