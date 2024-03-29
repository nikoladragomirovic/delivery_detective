import React from "react";

const Page = ({ setLoggedIn }) => {
  const handleLogOut = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch("http://127.0.0.1:5000/logout", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: new URLSearchParams({
          username: localStorage.getItem("username"),
          session_token: localStorage.getItem("session_token"),
        }),
      });
      if (response.ok) {
        const jsonResponse = await response.json();
        console.log("Logout successful", jsonResponse);
        localStorage.removeItem("username");
        localStorage.removeItem("session_token");
        setLoggedIn(false);
      } else {
        console.error("Logout failed");
      }
    } catch (error) {
      console.error("Error:", error);
    }
  };

  return (
    <div className="w-full font-dosis min-h-screen flex flex-col items-center justify-start">
      <div className="fixed flex flex-row justify-between px-10 py-6 w-full">
        <p className="py-1 px-4 text-emerald-500 border border-emerald-500 bg-emerald-50 font-extralight mb-4 text-xl rounded-3xl">
          {localStorage.getItem("username")}
        </p>
        <div
          className="py-1 px-4 text-emerald-500 border cursor-pointer border-emerald-500 bg-emerald-50 font-extralight mb-4 text-xl rounded-3xl"
          onClick={(e) => {
            handleLogOut(e);
          }}
        >
          Logout
        </div>
      </div>
    </div>
  );
};

export default Page;
