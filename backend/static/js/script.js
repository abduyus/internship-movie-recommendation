"use strict";

const movieFormEl = document.querySelector(".search-bar");
const movieInputEl = document.querySelector(".movie-form");
const cardParentEl = document.querySelector(".cards");
const cardEl = document.querySelectorAll(".card");
const loadingSpinner = document.querySelector(".spinner");
const placementText = document.querySelector(".placement-text");
const genreCheckboxes = document.querySelectorAll(".filter__checkbox");
const genreFilter = document.querySelector(".filter");

movieFormEl.addEventListener("submit", (e) => {
  e.preventDefault();
  const movieName = movieInputEl.value.trim();
  if (movieName) {
    getRecommendedMovies(movieName);
    // cardParentEl.innerHTML = "";
    loadingSpinner.classList.remove("hidden");
  }
});

const displayRecommendations = function (
  movieArr,
  msg = "Here are your top 5 Movie Recommendations"
) {
  loadingSpinner.classList.add("hidden");
  genreFilter.classList.remove("hidden");
  cardParentEl.innerHTML = "";
  placementText.textContent = msg;
  movieArr.forEach((movie) => {
    const markup = `
    <article class="card">
      <div class="card__data">
      <a href="${movie.homepage}" target="_blank" class="card__heading">${
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
    cardParentEl.firstElementChild
      .closest("article")
      .classList.add("card_first");
  });
};

const getRecommendedMovies = async function (movieName) {
  try {
    const res = await fetch(
      `http://127.0.0.1:5000/recommend?movie_title=${encodeURIComponent(
        movieName
      )}`
    );
    console.log(res);
    if (!res.ok) throw new Error(`An error has occurred: ${res.status}`);
    const data = await res.json();
    console.log(data);

    if (data.error) {
      console.error("Error:", data.error);
      displayRecommendations(data, data.error);
    } else {
      displayRecommendations(data);
    }
  } catch (error) {
    console.error("Network error:", error);
  }
};
let genres;

cardEl.forEach((card) => {
  genres = Array.from(card.querySelectorAll(".card__genre")).map(
    (genre) => genre.textContent
  );
});

console.log(genres);

genreCheckboxes.forEach((item) =>
  item.addEventListener("change", () => {
    const checkedGenres = Array.from(genreCheckboxes)
      .filter((checkbox) => checkbox.checked)
      .map((checkbox) => checkbox.nextElementSibling.textContent);

    checkedGenres.forEach((genre) => {
      console.log(genre);
      genres.includes(genre) ? console.log(true) : console.log(false);
    });
  })
);

const checkGenre = function (movieCard) {
  const checkedGenres = Array.from(genreCheckboxes)
    .filter((checkbox) => checkbox.checked)
    .map((checkbox) => checkbox.nextElementSibling.textContent);
  checkedGenres.forEach((genre) => {
    console.log(genre);
    genres.includes(genre) ? console.log(true) : console.log(false);
  });
  const genres = movieCard.querySelectorAll("card__genre").textContent;
  genres.includes();
};

const cardFilter = Array.from(document.querySelectorAll(".card"));

console.log(cardFilter);
cardFilter.filter();
