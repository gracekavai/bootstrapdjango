(function () {
  "use strict";

  const currencySelect = document.querySelector("[data-currency-select]");
  const statusElement = document.querySelector("[data-currency-status]");
  const prices = Array.from(document.querySelectorAll("[data-price-usd]"));
  const cacheKey = "pixelvillas-usd-rates-v1";
  const cacheMaxAge = 24 * 60 * 60 * 1000;
  const currencyLocales = {
    KES: "en-KE",
    USD: "en-US",
    EUR: "en-IE"
  };
  let rates;

  if (!currencySelect || prices.length === 0) {
    return;
  }

  function displayPrices(currency) {
    const rate = rates[currency];
    if (!Number.isFinite(rate) || rate <= 0) {
      throw new Error("Missing exchange rate for " + currency);
    }

    const formatter = new Intl.NumberFormat(currencyLocales[currency], {
      style: "currency",
      currency: currency,
      maximumFractionDigits: 0
    });

    prices.forEach(function (element) {
      const usdAmount = Number(element.dataset.priceUsd);
      if (!Number.isFinite(usdAmount) || usdAmount < 0) {
        throw new Error("Invalid property price");
      }
      element.textContent = formatter.format(usdAmount * rate);
    });
  }

  function useRates(rateData, isStale) {
    rates = { USD: 1, KES: rateData.KES, EUR: rateData.EUR };
    currencySelect.disabled = false;
    let savedCurrency = null;
    let storageWarning = "";
    try {
      savedCurrency = window.localStorage.getItem("pixelvillas-currency");
    } catch (error) {
      storageWarning = "Browser storage is unavailable; currency choice will not be saved.";
    }
    const currency = ["KES", "USD", "EUR"].includes(savedCurrency) ? savedCurrency : "KES";
    currencySelect.value = currency;
    displayPrices(currency);
    if (isStale) {
      statusElement.textContent = "Showing saved exchange rates; a live refresh was unavailable.";
    } else if (storageWarning) {
      statusElement.textContent = storageWarning;
    } else {
      statusElement.textContent = "Indicative rates. Updated daily.";
    }
  }

  function readCachedRates() {
    try {
      const cached = JSON.parse(window.localStorage.getItem(cacheKey));
      if (
        cached &&
        cached.rates &&
        Number.isFinite(cached.savedAt) &&
        Number.isFinite(cached.rates.KES) &&
        Number.isFinite(cached.rates.EUR)
      ) {
        return cached;
      }
    } catch (error) {
      try {
        window.localStorage.removeItem(cacheKey);
      } catch (storageError) {
        return null;
      }
    }
    return null;
  }

  currencySelect.disabled = true;
  statusElement.textContent = "Loading exchange rates...";

  const cachedRates = readCachedRates();
  const cachedIsFresh = cachedRates && Date.now() - cachedRates.savedAt < cacheMaxAge;

  if (cachedIsFresh) {
    useRates(cachedRates.rates, false);
  } else if (cachedRates) {
    useRates(cachedRates.rates, true);
  }

  if (!cachedIsFresh) {
    fetch("https://open.er-api.com/v6/latest/USD")
      .then(function (response) {
        if (!response.ok) {
          throw new Error("Exchange-rate service returned HTTP " + response.status);
        }
        return response.json();
      })
      .then(function (data) {
        const kesRate = data.rates && Number(data.rates.KES);
        const eurRate = data.rates && Number(data.rates.EUR);
        if (
          data.result !== "success" ||
          data.base_code !== "USD" ||
          !Number.isFinite(kesRate) ||
          kesRate <= 0 ||
          !Number.isFinite(eurRate) ||
          eurRate <= 0
        ) {
          throw new Error("Exchange-rate response did not contain valid KES and EUR rates");
        }
        const currentRates = { KES: kesRate, EUR: eurRate };
        let storageWarning = "";
        try {
          window.localStorage.setItem(
            cacheKey,
            JSON.stringify({ savedAt: Date.now(), rates: currentRates })
          );
        } catch (storageError) {
          storageWarning = "Rates loaded; this browser cannot cache them.";
        }
        useRates(currentRates, false);
        if (storageWarning) {
          statusElement.textContent = storageWarning;
        }
      })
      .catch(function (error) {
        if (cachedRates) {
          return;
        }
        rates = { USD: 1 };
        currencySelect.value = "USD";
        currencySelect.disabled = true;
        displayPrices("USD");
        statusElement.textContent =
          "Live rates are unavailable; prices are shown in USD. " + error.message;
      });
  }

  currencySelect.addEventListener("change", function () {
    try {
      displayPrices(currencySelect.value);
      try {
        window.localStorage.setItem("pixelvillas-currency", currencySelect.value);
      } catch (storageError) {
        statusElement.textContent = "Prices converted; this browser cannot save your currency choice.";
      }
    } catch (error) {
      statusElement.textContent = "Could not convert prices: " + error.message;
    }
  });
})();
