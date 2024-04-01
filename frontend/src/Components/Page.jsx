import React, { useState, useEffect } from "react";

const Page = ({ setLoggedIn }) => {
  const [restaurants, setRestaurants] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [settings, setSettings] = useState(false);

  const serviceBackgroundColors = {
    Wolt: "bg-[#009DE0]",
    Glovo: "bg-[#FFC244]",
    MisterD: "bg-[#BC2C3D]",
  };

  const serviceForegroundColors = {
    Wolt: "text-white",
    Glovo: "text-[#00A082]",
    MisterD: "text-white",
  };

  const serviceBadges = {
    Wolt: "/plus.svg",
    Glovo: "/prime.svg",
  };

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
      <div className="fixed bg-white border-b rounded-b-2xl border-gray-500 flex flex-row justify-around py-4 w-full">
        <div className="py-1 relative px-4 cursor-pointer flex items-center justify-center text-gray-500 border border-gray-500 bg-gray-100 font-extralight text-xl rounded-3xl">
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
              className="py-1 px-4 text-gray-500 border cursor-pointer border-gray-500 bg-gray-100 font-extralight text-xl rounded-3xl"
            >
              Logout
            </p>
            <p className="py-1 px-4 text-gray-500 border cursor-pointer border-gray-500 bg-gray-100 font-extralight text-xl rounded-3xl">
              Settings
            </p>
          </div>
        </div>
        <input
          type="text"
          placeholder="Search by name"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="border caret-gray-400 text-gray-500 border-gray-500 font-extralight text-lg px-4 py-1 focus:outline-none rounded-3xl"
        />
      </div>
      <div className="pt-20 grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3">
        {filteredRestaurants.map((restaurant, index) => (
          <div
            key={index}
            className="border border-gray-500 p-5 m-4 bg-gray-50 rounded-3xl"
          >
            <h2 className="text-xl mb-2 text-gray-600 font-bold">
              {restaurant.name}
            </h2>
            <div className="flex flex-row justify-start space-x-6 text-lg items-start">
              {restaurant.services.map((service, index) => (
                <a
                  key={index}
                  href={service.link}
                  target="_blank"
                  rel="noreferrer noopener"
                  className="flex flex-col items-center justify-center"
                >
                  <p
                    className={`${
                      serviceBackgroundColors[service.name]
                    } py-1 px-4 rounded-3xl font-semibold ${
                      serviceForegroundColors[service.name]
                    }`}
                  >
                    {service.name}
                  </p>
                  <p className="text-gray-600">{service.price}</p>
                </a>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Page;
