import React, { useState, useEffect } from "react";

const Page = ({ setLoggedIn }) => {
  const [restaurants, setRestaurants] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [settings, setSettings] = useState(false);

  useEffect(() => {
    async function fetchRestaurants() {
      try {
        const response = await fetch("http://127.0.0.1:5000/restaurants", {
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
          const data = await response.json();
          setRestaurants(data);
        } else {
          console.error("Failed to fetch restaurants");
        }
      } catch (error) {
        console.error("Error:", error);
      }
    }

    fetchRestaurants();
  }, []);

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

  const filteredRestaurants = restaurants.filter((restaurant) =>
    restaurant.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div
      onClick={() => {
        setSettings(false);
      }}
      className="w-full font-dosis min-h-screen flex flex-col items-center justify-start"
    >
      <div className="fixed bg-white border-b rounded-b-2xl border-emerald-500 flex flex-row justify-around py-4 w-full">
        <div className="py-1 relative px-4 cursor-pointer flex items-center justify-center text-emerald-500 border border-emerald-500 bg-emerald-50 font-extralight text-xl rounded-3xl">
          <p
            onClick={(e) => {
              e.stopPropagation();
              setSettings(!settings);
            }}
          >
            {localStorage.getItem("username")}
          </p>
          <div
            className={`${
              settings ? "opacity-100" : "opacity-0"
            } absolute top-full space-y-4 mt-8 px-6 py-4 border rounded-3xl bg-white duration-300`}
          >
            <p
              onClick={(e) => {
                handleLogOut(e);
              }}
              className="py-1 px-4 text-emerald-500 border cursor-pointer border-emerald-500 bg-emerald-50 font-extralight text-xl rounded-3xl"
            >
              Logout
            </p>
            <p className="py-1 px-4 text-emerald-500 border cursor-pointer border-emerald-500 bg-emerald-50 font-extralight text-xl rounded-3xl">
              Settings
            </p>
          </div>
        </div>
        <input
          type="text"
          placeholder="Search by name"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="border border-gray-500 font-light px-4 py-1 focus:outline-none rounded-3xl"
        />
      </div>
      <div className="pt-20 grid grid-cols-3">
        {filteredRestaurants.map((restaurant, index) => (
          <div
            key={index}
            className="border border-gray-300 p-4 m-4 rounded-md"
          >
            <h2 className="text-lg font-semibold">{restaurant.name}</h2>
            {restaurant.services.map((service, index) => (
              <div key={index} className="flex flex-row space-x-2">
                <p>{service.name}</p>
                <p>{service.price}</p>
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
};

export default Page;
