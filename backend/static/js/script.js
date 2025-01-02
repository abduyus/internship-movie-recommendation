"use strict";

const movieNameEl = document.querySelector(".movie-form");

console.log(movieNameEl);
console.log(encodeURIComponent("iron man"));
const getRecommendedMovies = async function (movieName) {
  try {
    const res = await fetch(
      `http://127.0.0.1:5000/recommend?movie=${movieName}`
    );
    if (!res.ok) throw new Error(`An error has occured: ${res.status}`);
    const data = await res.json();
    console.log(data);
  } catch (error) {
    console.error("Network error:", error);
  }
};

getRecommendedMovies("superman");
