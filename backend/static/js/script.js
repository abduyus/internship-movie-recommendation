"use strict";

const movieFormEl = document.querySelector(".search-bar");
const movieInputEl = document.querySelector(".movie-form");
const cardParentEl = document.querySelector(".cards");
movieFormEl.addEventListener("submit", (e) => {
  e.preventDefault();
  const movieName = movieInputEl.value.trim();
  if (movieName) {
    getRecommendedMovies(movieName);
  }
});

const displayRecommendations = function (movieArr) {
  movieArr.forEach((movie) => {
    const markup = `
    <article class="card">
      <div class="card__data">
      <a href="${movie.homepage}" class="card__heading">${
      movie.original_title
    }</a>
      <div class="card__genres">
        ${movie.genres_arr
          .map(
            (genre) =>
              `<span class="card__genre ${genre.toLowerCase()}">${genre}</span>`
          )
          .join("")}
      </div>
      <h4 class="card__subheading">${movie.tagline || " "}</h4>
      <p class="card__row"><span>⭐</span>${movie.vote_average}</p>
      <p class="card__row"><span>📅</span>${movie.release_date.substring(
        0,
        4
      )}</p>
      <p class="card__row"><span>🗣️</span>${movie.director}</p>
      </div>
    </article>
    `;
    cardParentEl.insertAdjacentHTML("beforeend", markup);
  });
};

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

    if (data.error) {
      console.error("Error:", data.error);
    } else {
      displayRecommendations(data);
    }
  } catch (error) {
    console.error("Network error:", error);
  }
};
