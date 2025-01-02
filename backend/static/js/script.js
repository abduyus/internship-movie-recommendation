"use strict";

const movieNameEl = document.querySelector(".movie-form");

console.log(movieNameEl);
console.log(encodeURIComponent("iron man"));
const getRecommendedMovies = async function (movieName) {
  const res = await fetch(`http://127.0.0.1:8000/recommend?movie=${movieName}`);
  const data = await res.json();
  console.log(data);
};

getRecommendedMovies("superman");
