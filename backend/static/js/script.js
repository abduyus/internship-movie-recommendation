"use strict";

const movieFormEl = document.querySelector(".search-bar");
const movieInputEl = document.querySelector(".movie-form");

movieFormEl.addEventListener("submit", (e) => {
  e.preventDefault();
  const movieName = movieInputEl.value.trim();
  if (movieName) {
    getRecommendedMovies(movieName);
  }
});

const getRecommendedMovies = async function (movieName) {
  try {
    const res = await fetch(
      `http://127.0.0.1:5000/recommend?movie_title=${encodeURIComponent(
        movieName
      )}`
    );
    if (!res.ok) throw new Error(`An error has occurred: ${res.status}`);
    const data = await res.json();
    console.log(data);
    displayRecommendations(data);
  } catch (error) {
    console.error("Network error:", error);
  }
};
