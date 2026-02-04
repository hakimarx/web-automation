/*
Author: Kevin Kurnia Wikarta
Version: 1.0.0
Website: https://kevkw.id/
Contact: kevkw.work@gmail.com
File: Js Form Hanlder
*/

function submitLoader(formId = "#form_input") {
  let form = $(formId);
  let submitButton = form.find("button[type=submit]");
  let cancelButton = form.find(".btn-cancel");

  let buttonText = submitButton.html();

  function show() {
    submitButton
      .addClass("btn-load")
      .attr("disabled", true)
      .data("btn-text", buttonText)
      .html(
        `<span class="d-flex justify-content-center align-items-center">
          <span class="spinner-border flex-shrink-0"></span>
          <span class="ms-2">Loading...</span>
        </span>`
      );

    cancelButton.attr("disabled", true);
  }

  function hide() {
    let buttonText = submitButton.data("btn-text") || "Simpan";
    submitButton
      .removeClass("btn-load")
      .removeAttr("disabled")
      .html(buttonText);
    cancelButton.removeAttr("disabled");
  }

  return {
    show,
    hide,
  };
}

function handleFormSubmit(selector) {
  function init() {
    const _this = this;

    $(selector).on("submit", function (e) {
      e.preventDefault();

      const _form = this;

      $.ajax({
        url: _form.action,
        method: _form.method,
        headers: {
          "KV-TOKEN": $('meta[name="csrf-token"]').attr("content"),
        },
        data: new FormData(_form),
        contentType: false,
        processData: false,
        beforeSend: function () {
          $(_form).find(".is-invalid").removeClass("is-invalid");
          $(_form).find(".invalid-feedback").remove();
          submitLoader(selector).show();
        },
        complete: function () {
          submitLoader(selector).hide();
        },
        success: function (res) {
          if (_this.onSuccessCallback) {
            _this.onSuccessCallback(res);
          }
        },
        error: function (err) {
          var errors = err.responseJSON?.errors;

          if (_this.onErrorCallback) {
            _this.onErrorCallback(err);
          }

          if (errors) {
            for (let [key, message] of Object.entries(errors)) {
              $(`[name="${key}"]`)
                .addClass("is-invalid")
                .parent()
                .append(`<div class="invalid-feedback">${message}</div>`);
            }
          }
        },
      });
    });
  }

  function onSuccess(cb, runDefault = true) {
    this.onSuccessCallback = cb;
    this.runDefaultSuccessCallback = runDefault;

    return this;
  }

  function onError(cb) {
    this.onErrorCallback = cb;

    return this;
  }

  function setDataTable(id) {
    this.dataTableId = id;

    return this;
  }

  return {
    init,
    runDefaultSuccessCallback: true,
    onSuccess,
    onError,
    setDataTable,
  };
}

function handleAjax(url, method = "GET") {
  let onSuccessCallback = function () {};
  let onErrorCallback = function () {};

  function onSuccess(cb) {
    onSuccessCallback = cb;

    return this;
  }

  function onError(cb) {
    onErrorCallback = cb;

    return this;
  }

  function execute() {
    $.ajax({
      url: url,
      method: method,
      headers: {
        "KV-TOKEN": $('meta[name="csrf-token"]').attr("content"),
      },
      beforeSend: function () {
        showLoading();
      },
      complete: function () {
        hideLoading();
      },
      success: function (res) {
        onSuccessCallback(res);
      },
      error: function (err) {
        onErrorCallback(err);
      },
    });
  }

  return {
    execute,
    onSuccess,
    onError,
  };
}
