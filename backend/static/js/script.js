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

const displayRecommendations = function (movieStr) {
  // console.log(typeof movieStr);

  console.log(movieStr);
  // const recommendationsEl = document.querySelector(".recommendations");
  // recommendationsEl.innerHTML = "";

  // movieList.forEach((movie) => {
  //   const movieEl = document.createElement("div");
  //   movieEl.classList.add("movie");

  //   const titleEl = document.createElement("h3");
  //   titleEl.textContent = movie.title;
  //   movieEl.appendChild(titleEl);

  //   const overviewEl = document.createElement("p");
  //   overviewEl.textContent = movie.overview;
  //   movieEl.appendChild(overviewEl);

  //   recommendationsEl.appendChild(movieEl);
  // });
};

const getRecommendedMovies = async function (movieName) {
  try {
    const res = await fetch(
      `http://127.0.0.1:5000/recommend?movie_title=${encodeURIComponent(
        movieName
      )}`
    );
    if (!res.ok) throw new Error(`An error has occurred: ${res.status}`);
    // const data = await res.json();
    const data = await res.json();
    console.log(data);

    displayRecommendations(data);
  } catch (error) {
    console.error("Network error:", error);
  }
};
