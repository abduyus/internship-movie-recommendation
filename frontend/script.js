"use strict";

const movieNameEl = document.querySelector(".movie-form");

console.log(movieNameEl);

const getRecommendedMovies = async function (movieName) {
  const res = await fetch(
    `http://127.0.0.1:5000/recommend?movie=${encodeURIComponent(movieName)}`
  );
  const data = await res.json();
  console.log(data);
};

getRecommendedMovies("iron man");

app.get("/recommend", (req, res) => {
  res.setHeader("Access-Control-Allow-Origin", "*");

  // your existing code
});
