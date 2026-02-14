import React from "react";
function Transactions() {
  const transactions = [
    { id: 1, date: "10 Feb 2026", merchant: "Amazon", amount: "-₹1,200" },
    { id: 2, date: "09 Feb 2026", merchant: "Salary", amount: "+₹45,000" },
    { id: 3, date: "08 Feb 2026", merchant: "Swiggy", amount: "-₹350" },
  ];

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Transactions</h2>

      <div className="bg-white shadow rounded-lg p-6">
        <table className="w-full">
          <thead>
            <tr className="text-left border-b">
              <th className="pb-2">Date</th>
              <th className="pb-2">Merchant</th>
              <th className="pb-2">Amount</th>
            </tr>
          </thead>
          <tbody>
            {transactions.map((txn) => (
              <tr key={txn.id} className="border-b">
                <td className="py-3">{txn.date}</td>
                <td>{txn.merchant}</td>
                <td className="font-semibold">{txn.amount}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default Transactions;
