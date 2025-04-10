(function ($) {
  "use strict";

  if ($(".countdown-one__list").length) {
    let deadLine = new Date(Date.parse(new Date()) + 12 * 24 * 60 * 60 * 1000);
    $(".countdown-one__list").countdown({
      date: deadLine,
      render: function (date) {
        this.el.innerHTML =
          "<li> <div class='days'> <i>" +
          date.days +
          "</i> <span>Days</span> </div> </li>" +
          "<li> <div class='hours'> <i>" +
          date.hours +
          "</i> <span>Hours</span> </div> </li>" +
          "<li> <div class='minutes'> <i>" +
          date.min +
          "</i> <span>Minutes</span> </div> </li>" +
          "<li> <div class='seconds'> <i>" +
          date.sec +
          "</i> <span>Seconds</span> </div> </li>";
      }
    });
  }
  if ($(".scroll-to-target").length) {
    $(".scroll-to-target").on("click", function () {
      var target = $(this).attr("data-target");
      // animate
      $("html, body").animate(
        {
          scrollTop: $(target).offset().top
        },
        1000
      );

      return false;
    });
  }
  if ($(".contact-form-validated").length) {
    $(".contact-form-validated").validate({
      // initialize the plugin
      rules: {
        name: {
          required: true
        },
        email: {
          required: true,
          email: true
        },
        message: {
          required: true
        },
        subject: {
          required: true
        }
      },
      submitHandler: function (form) {
        // sending value with ajax request
        $.post(
          $(form).attr("action"),
          $(form).serialize(),
          function (response) {
            $(form).parent().find(".result").append(response);
            $(form).find('input[type="text"]').val("");
            $(form).find('input[type="email"]').val("");
            $(form).find("textarea").val("");
          }
        );
        return false;
      }
    });
  }
  // mailchimp form
  if ($(".mc-form").length) {
    $(".mc-form").each(function () {
      var Self = $(this);
      var mcURL = Self.data("url");
      var mcResp = Self.parent().find(".mc-form__response");

      Self.ajaxChimp({
        url: mcURL,
        callback: function (resp) {
          // appending response
          mcResp.append(function () {
            return '<p class="mc-message">' + resp.msg + "</p>";
          });
          // making things based on response
          if (resp.result === "success") {
            // Do stuff
            Self.removeClass("errored").addClass("successed");
            mcResp.removeClass("errored").addClass("successed");
            Self.find("input").val("");

            mcResp.find("p").fadeOut(10000);
          }
          if (resp.result === "error") {
            Self.removeClass("successed").addClass("errored");
            mcResp.removeClass("successed").addClass("errored");
            Self.find("input").val("");

            mcResp.find("p").fadeOut(10000);
          }
        }
      });
    });
  }
  if ($(".video-popup").length) {
    $(".video-popup").magnificPopup({
      type: "iframe",
      mainClass: "mfp-fade",
      removalDelay: 160,
      preloader: true,

      fixedContentPos: false
    });
  }
  if ($(".img-popup").length) {
    var groups = {};
    $(".img-popup").each(function () {
      var id = parseInt($(this).attr("data-group"), 10);

      if (!groups[id]) {
        groups[id] = [];
      }

      groups[id].push(this);
    });

    $.each(groups, function () {
      $(this).magnificPopup({
        type: "image",
        closeOnContentClick: true,
        closeBtnInside: false,
        gallery: {
          enabled: true
        }
      });
    });
  }
  if ($(".main-menu__list").length) {
    // dynamic current class
    let mainNavUL = $(".main-menu__list");
    dynamicCurrentMenuClass(mainNavUL);
  }
  if ($(".main-menu").length && $(".mobile-nav__container").length) {
    let navContent = document.querySelector(".main-menu").innerHTML;
    let mobileNavContainer = document.querySelector(".mobile-nav__container");
    mobileNavContainer.innerHTML = navContent;
  }
  if ($(".sticky-header__content").length) {
    let navContent = document.querySelector(".main-menu").innerHTML;
    let mobileNavContainer = document.querySelector(".sticky-header__content");
    mobileNavContainer.innerHTML = navContent;
  }
  if ($(".mobile-nav__container .main-menu__list").length) {
    let dropdownAnchor = $(
      ".mobile-nav__container .main-menu__list .dropdown > a"
    );
    dropdownAnchor.each(function () {
      let self = $(this);
      let toggleBtn = document.createElement("BUTTON");
      toggleBtn.setAttribute("aria-label", "dropdown toggler");
      toggleBtn.innerHTML = "<i class='fa fa-angle-down'></i>";
      self.append(function () {
        return toggleBtn;
      });
      self.find("button").on("click", function (e) {
        e.preventDefault();
        let self = $(this);
        self.toggleClass("expanded");
        self.parent().toggleClass("expanded");
        self.parent().parent().children("ul").slideToggle();
      });
    });
  }
  if ($(".mobile-nav__toggler").length) {
    $(".mobile-nav__toggler").on("click", function (e) {
      e.preventDefault();
      $(".mobile-nav__wrapper").toggleClass("expanded");
      $("body").toggleClass("locked");
    });
  }
  if ($(".search-toggler").length) {
    $(".search-toggler").on("click", function (e) {
      e.preventDefault();
      $(".search-popup").toggleClass("active");
      $('.mobile-nav__wrapper').removeClass('expanded');
      $("body").toggleClass("locked");
    });
  }
  if ($(".error-toggler").length) {
    $(".error-toggler").on("click", function (e) {
      e.preventDefault();
      $(".error-popup").toggleClass("active");
      $('.mobile-nav__wrapper').removeClass('expanded');
      $("body").toggleClass("locked");
    });
  }
  if ($(".error-toast").length) {
    $(".error-toast button").on("click", function (e) {
      e.preventDefault();
      $(".error-popup").toggleClass("active");
      $('.mobile-nav__wrapper').removeClass('expanded');
      $("body").toggleClass("locked");      
    });
  }
  if ($(".mini-cart__toggler").length) {
    CartEvents();
  }
  if ($(".odometer").length) {
    $(".odometer").appear(function (e) {
      var odo = $(".odometer");
      odo.each(function () {
        var countNumber = $(this).attr("data-count");
        $(this).html(countNumber);
      });
    });
  }
  if ($(".dynamic-year").length) {
    let date = new Date();
    $(".dynamic-year").html(date.getFullYear());
  }
  if ($(".wow").length) {
    var wow = new WOW({
      boxClass: "wow", // animated element css class (default is wow)
      animateClass: "animated", // animation css class (default is animated)
      mobile: true, // trigger animations on mobile devices (default is true)
      live: true // act on asynchronously loaded content (default is true)
    });
    wow.init();
  }
  if ($("#donate-amount__predefined").length) {
    let donateInput = $("#donate-amount");
    $("#donate-amount__predefined")
      .find("li")
      .on("click", function (e) {
        e.preventDefault();
        let amount = $(this).find("a").text();
        donateInput.val(amount);
        $("#donate-amount__predefined").find("li").removeClass("active");
        $(this).addClass("active");
      });
  }
  $("#accordion .collapse").on("shown.bs.collapse", function () {
    $(this).prev().addClass("active");
    $(this).prev().parent().addClass("active");
    if ($("#submit-order")) {
      if (compareElements($(this).prev(), $('h2[name="para-title-order"]'))) {
        const submitOrderWithContext = $(this).prev().length ? 
          submitOrderEvent.bind($(this).prev()[0]) :
          null;
        if (submitOrderWithContext)
            $('#submit-order').off('click').on('click', submitOrderWithContext);
      }
      if (compareElements($(this).prev(), $('h2[name="para-title-payment"]'))) {
        const createPaymentWithContext = $(this).prev().length ?
          createPaymentEvent.bind($(this).prev()[0]) : 
          null;
        if (createPaymentWithContext)
          $('#submit-order').off('click').on('click', createPaymentWithContext);
      }
    }
  });
  $("#accordion .collapse").on("hidden.bs.collapse", function () {
    $(this).prev().removeClass("active");
    $(this).prev().parent().removeClass("active");
  });
  $("#accordion").on("hide.bs.collapse show.bs.collapse", (e) => {
    $(e.target).prev().find("i:last-child").toggleClass("fa-plus fa-minus");
  });
  // $(".add").on("click", function () {
  //   if ($(this).prev().val() < 999) {
  //     $(this)
  //       .prev()
  //       .val(+$(this).prev().val() + 1);
  //     const $form = $(this).parent().find("form[name='cart-form']")[0];
  //     updateCart($form, $(this).data('url'))
  //       .then(cartItem => {
  //         updateCartCount(
  //           document.querySelector(`#cart-count-${cartItem.id}`),
  //           cartItem.quantity
  //         );
  //         updateCartCount(
  //           document.querySelector(".topbar__buttons .cart-count"),
  //           cartItem.total_quantity
  //         );
  //       })
  //       .catch(error => {
  //         console.log(error);
  //       });
  //   }
  // });
  // $(".sub").on("click", function () {
  //   if ($(this).next().val() > 1) {
  //     $(this)
  //       .next()
  //       .val(+$(this).next().val() - 1);
  //     const $form = $(this).parent().find("form[name='cart-form']")[0];
  //     updateCart($form, $(this).data('url'))
  //       .then(cartItem => {
  //         updateCartCount(
  //           document.querySelector(`#cart-count-${cartItem.id}`),
  //           cartItem.quantity
  //         );
  //         updateCartCount(
  //           document.querySelector(".topbar__buttons .cart-count"),
  //           cartItem.total_quantity
  //         );
  //       })
  //       .catch(error => {
  //         console.log(error);
  //       });
  //   }
  // });
  if ($(".tabs-box").length) {
    $(".tabs-box .tab-buttons .tab-btn").on("click", function (e) {
      e.preventDefault();
      var target = $($(this).attr("data-tab"));

      if ($(target).is(":visible")) {
        return false;
      } else {
        target
          .parents(".tabs-box")
          .find(".tab-buttons")
          .find(".tab-btn")
          .removeClass("active-btn");
        $(this).addClass("active-btn");
        target
          .parents(".tabs-box")
          .find(".tabs-content")
          .find(".tab")
          .fadeOut(0);
        target
          .parents(".tabs-box")
          .find(".tabs-content")
          .find(".tab")
          .removeClass("active-tab");
        $(target).fadeIn(300);
        $(target).addClass("active-tab");
      }
    });
  }
  if ($("form[name='products-search']").length) {
    $("form[name='products-search']").on("submit", function (e) {
      e.preventDefault();
      $.ajax({
        type: 'POST',
        url: getBaseURL(location.toString()),
        data: getFilterAndSorting(),
        contentType: false,
        processData: false,
        success: (_) => {
          location.reload();
        },
        error: (error) => handleException(error)
      });
    });
  }
  if ($("form[name='main-search']").length) {
    $("form[name='main-search']").on("submit", function (e) {
      e.preventDefault();
      const $form = e.currentTarget;
      const $url = $form.action;
      $.ajax({
        type: 'POST',
        url: $url,
        data: new FormData($form),
        contentType: false,
        processData: false,
        success: (_) => {
          // location.reload();
          window.location.replace($url);
        },
        error: (error) => handleException(error)
      });
    });
  }
  if ($(".range-slider-price").length) {
    var priceRange = document.getElementById("range-slider-price");

    noUiSlider.create(priceRange, {
      start: [30, 150],
      limit: 200,
      behaviour: "drag",
      connect: true,
      range: {
        min: 10,
        max: 200
      }
    });

    var limitFieldMin = document.getElementById("min-value-rangeslider");
    var limitFieldMax = document.getElementById("max-value-rangeslider");

    priceRange.noUiSlider.on("update", function (values, handle) {
      (handle ? $(limitFieldMax) : $(limitFieldMin)).text(values[handle]);
    });
  }
  if ($("select[class='selectpicker']").length) {
    $("select[class='selectpicker']").on("change", function (e) {
      e.preventDefault();
      $.ajax({
        type: 'POST',
        url: getBaseURL(location.toString()),
        data: getFilterAndSorting(),
        contentType: false,
        processData: false,
        success: (_) => {
          location.reload();
        },
        error: (error) => handleException(error)
      });
    });
  }
  if ($(".signup__toggler").length) {
    $(".signup__toggler").on("click", function (e) {
      e.preventDefault();
      updateLoginForm('/accounts/signup/');
    });
  }
  if ($(".login__toggler").length) {
    $(".login__toggler").on("click", function (e) {
      e.preventDefault();
      updateLoginForm('/accounts/login/');
    });
  }
  if ($(".login-form").length) {
    $(".login-form").on("click", function (e) {
      e.preventDefault();
      // Скрывать форму по клику в любом месте экрана
      // if ($(e.target).parents().closest('form').html()) return;
      // $(".login-form").toggleClass("shown");
      // $('.mobile-nav__wrapper').removeClass('shown');
      // $("body").toggleClass("locked");
    });
  }
  if ($("a[name='add-to-cart']").length) {
    $("a[name='add-to-cart']").on("click", function (e) {
      e.preventDefault();
      const $form = e.currentTarget.querySelector("form[name='add-to-cart-form']");
      updateCart($form, $form.action)
        .then(cartItem => {
          updateCartCount(
            e.currentTarget.querySelector("span[class='cart-count']"),
            cartItem.quantity
          );
          updateCartCount(
            document.querySelector(".topbar__buttons .cart-count"),
            cartItem.total_quantity
          );
          updateMiniCart(`${location.origin}/cart/mini`)
            .then(html => {
              document.querySelector('.mini-cart').outerHTML = html;
              CartEvents();
            })
            .catch(error => handleException(error));
        })
        .catch(error => handleException(error))
    });  
  }
  if ($("#submit-order")) {
    $("#submit-order").on("click", function() {
      const submitOrder = submitOrderEvent.bind(this);
      submitOrder();
    });
  }
  if ($("#map").length) {
    ymaps.ready(function () {
      var myMap = new ymaps.Map("map", {
              center: [45.006444, 39.015782],
              zoom: 17
          }, {
              searchControlProvider: 'yandex#search'
          }),
  
          myPlacemark = new ymaps.Placemark(myMap.getCenter(), {
              hintContent: 'Свобода 23',
              balloonContent: 'Краснодар ул.Воронежская 42'
          }, {
              iconLayout: 'default#image',
              iconImageHref: 'static/images/logo-main.png',
              iconImageSize: [45, 45],
              // Смещение левого верхнего угла иконки относительно
              // её "ножки" (точки привязки).
              // iconImageOffset: [-5, -38]
          });

  
      myMap.geoObjects.add(myPlacemark);  
      myMap.behaviors.disable('scrollZoom');

    });
  }
  if ($("a[name='make-order']").length) {
    $("a[name='make-order']").on("click", function (e) {
      e.preventDefault();
      const $url = $(e.currentTarget).data('url');
      if (!$url) return;

      $.ajax({
        url: $url,
        success: (response) => {
          const selectDepartmentsForm = $(".select-departments-form");
          selectDepartmentsForm.html(response);

          // Отобразить форму с возможностью закрытия по клику в любом месте экрана:
          // selectDepartmentsForm.toggleClass("shown");
          // $('.mobile-nav__wrapper').removeClass('shown');
          // $("body").toggleClass("locked");

          // Отобразить форму с возможностью закрытия только по клику на крестик:
          selectDepartmentsForm.addClass("shown");
          $('.mobile-nav__wrapper').removeClass('shown');
          $("body").addClass("locked");

          // Закрываем форму по клику на крестик:
          $(".select-departments-form i.organik-icon-close").click(e => {
            e.preventDefault();
            selectDepartmentsForm.removeClass("shown");
            $('.mobile-nav__wrapper').addClass('shown');
            $("body").removeClass("locked");
          });

        }
      });

    });
  }
  function waitForDialog(element, timeout = 60000) {
    let elapsed = 0;
    const interval = 300;
    const start = Date.now();

    const check = () => {
      const el = document.querySelector(element);
      if (el != null) {
        return detectPaymentDialogClosed(element);
      }
      elapsed = Date.now() - start;
      if (elapsed >= timeout) {
          return;
      }
      setTimeout(check, interval);
    }

    check();
  }
  function isEmpty(obj) {
    return Object.keys(obj).length === 0;
  }
  function compareElements($elements1, $elements2) {
    if ($elements1.length !== $elements2.length) {
      return false;
    }
  
    return $elements1.toArray().every((el1, index) => el1.isEqualNode($elements2.get(index)));
  }
  function dynamicCurrentMenuClass(selector) {
    let FileName = window.location.href.split("/").reverse()[0];

    selector.find("li").each(function () {
      let anchor = $(this).find("a");
      if ($(anchor).attr("href") == FileName) {
        $(this).addClass("current");
      }
    });
    // if any li has .current elmnt add class
    selector.children("li").each(function () {
      if ($(this).find(".current").length) {
        $(this).addClass("current");
      }
    });
    // if no file name return
    if ("" == FileName) {
      selector.find("li").eq(0).addClass("current");
    }
  }
  function getFilterAndSorting() {
    const $form = document.querySelector("form[name='products-search']");
    const formData = new FormData($form);
    const sortSelector = document.querySelector("select[class='selectpicker']");
    const sort_by_product_name = sortSelector.options[sortSelector.selectedIndex].value;
    if (sort_by_product_name)
      formData.append('sort_by_product_name', sort_by_product_name);

    return formData;  
  }
  function decimalFormat(number, fixed=2) {
    return number
      .toFixed(fixed)
      .replace('.', ',');
      // .replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
  }
  function getBaseURL(urlString) {
    const url = new URL(urlString);
    return `${url.pathname}`;
  }
  function isObject(value) {
    return value !== null && typeof value === 'object';
  }
  function thmSwiperInit() {
    // swiper slider
    const swiperElm = document.querySelectorAll(".thm-swiper__slider");
    swiperElm.forEach(function (swiperelm) {
      const swiperOptions = JSON.parse(swiperelm.dataset.swiperOptions);
      let thmSwiperSlider = new Swiper(swiperelm, swiperOptions);
    });
  }
  function thmTinyInit() {
    // tiny slider
    const tinyElm = document.querySelectorAll(".thm-tiny__slider");
    tinyElm.forEach(function (tinyElm) {
      const tinyOptions = JSON.parse(tinyElm.dataset.tinyOptions);
      let thmTinySlider = tns(tinyOptions);
    });
  }
  function isUserAuthenticated() {
    $.ajax({
      url: '/is_user_authenticated/',
      success: (response) => {
        response.is_authenticated
      }
    });
  }
  function updateLoginForm(url) {
    $.ajax({
      url: url,
      success: (response) => {
        const loginForm = $(".login-form");
        loginForm.html(response);

        // Отобразить форму с возможностью закрытия по клику в любом месте экрана:
        // loginForm.toggleClass("shown");
        // $("body").toggleClass("locked");

        // Отобразить форму с возможностью закрытия только по клику на крестик:
        loginForm.addClass("shown");
        $('.mobile-nav__wrapper').removeClass('shown');
        $("body").addClass("locked");

        eventLoginForm();
      }
    });
  }
  function eventLoginForm() {
    $('#signup-form button').click(e => {
      e.preventDefault();
      const loginForm = $(".login-form");
      const form = $('#signup-form');
      $.ajax({
        type: 'POST',
        url: form.attr('action'),
        data: form.serialize(),
        success: (response) => {
          if (!isObject(response)) {
            loginForm.html(response);
            eventLoginForm()
          } else {
            if ('is_authenticated' in response && response.is_authenticated) {
              location.reload();
            } else {
              // Скрывать форму:
              // loginForm.toggleClass("shown");
              // $('.mobile-nav__wrapper').removeClass('shown');
              // $("body").toggleClass("locked");
            }
          }
        },
        error: (errors => handleException(errors))
      });
    });
    // Закрываем форму по клику на крестик:
    $(".login-form i.organik-icon-close").click(e => {
      e.preventDefault();
      const loginForm = $(".login-form");
      loginForm.removeClass("shown");
      $('.mobile-nav__wrapper').addClass('shown');
      $("body").removeClass("locked");
    });

  }
  function updateCart($form, url) {
    let formData = new FormData();
    if ($form instanceof FormData) {
      formData = $form;
    } else {
      formData = new FormData($form);
    }
    return new Promise((resolve, reject) => {
      $.ajax({
        type: 'POST',
        url: url,
        data: formData,
        contentType: false,
        processData: false,
        success: (result) => {
          let cartItem = undefined;
          if (typeof result !== "string") {
            cartItem = result.find(_=>true);
            $($form).find('input[name="update"]')?.val(cartItem.update);
          }
          resolve(cartItem);
        },
        error: (error => reject(error))
      });
    });
  }
  function updateMiniCart(url) {
    return new Promise((resolve, reject) => {
      $.ajax({
        type: 'GET',
        url: url,
        success: (html) => {
          resolve(html);
        },
        error: (error => reject(error))
      });
    });
  }
  function updateCartCount(target, quantity=0) {
    if (target) {
      if (!quantity)
      target.style.display = 'none';
      else {
        target.style.display = 'flex';
        target.innerText = quantity;
      }
    }
  }
  function updateCartQuantity(target, quantity=0) {
    if (target) {
      if (!quantity) {
        target.value = 1;
      } else {
        target.value = quantity;
      }
    }
  }
  function CartEvents() {
    $(".mini-cart__toggler").off("click");
    $(".add").off("click"); $(".sub").off("click");
    $('.quantity-box input').off('change');
    $('.addto-cart-box button').off('click');

    $(".mini-cart__toggler").on("click", function (e) {
      e.preventDefault();
      if (location.pathname != '/cart/') {
        $(".mini-cart").toggleClass("expanded");
        $('.mobile-nav__wrapper').removeClass('expanded');
        $("body").toggleClass("locked");
      }
    });
    $(".add").on("click", function () {
      if ($(this).prev().val() < 999) {
        $(this)
          .prev()
          .val(+$(this).prev().val()+1);
        handleCartItems($(this));
      }
    });
    $(".sub").on("click", function () {
      if ($(this).next().val() > 1) {
        $(this)
          .next()
          .val(+$(this).next().val()-1);
        handleCartItems($(this));
      }
    });
    $('.quantity-box input').on('change', (e) => {
      e.preventDefault();
      const quantity = $(e.currentTarget).val();
      if (0 < +quantity < 999) {
        $(e.currentTarget).parents('.quantity-box').find('form[name="cart-form"] > input').each((_, el)=>{
          if (el.name == 'quantity') $(el).val(quantity);
          if (el.name == 'update') $(el).val(0);
        });
        handleCartItems($(e.currentTarget));
      }
    });
    $('.addto-cart-box button').on('click', (e) => {
      e.preventDefault();
      const target = $(e.currentTarget);
      const inCartQuantity = +target.parent().parent().find("div[name='cart_quantity']")?.text() || 0;
      const $formData = new FormData();
      const $form = target.parent().parent().find("form[name='cart-form']");
      $.each($form.find('input'), (_, el) => {
        if (el.name === 'quantity') {
          $formData.append(el.name, el.value-inCartQuantity);
        } else {
          $formData.append(el.name, el.value);
        }
      });
      let url = target.data('url');
      if ($formData.get('quantity') <= 0) 
        url = url.replace('update', 'remove');
      updateCart($formData, url)
        .then(_ => {
          location.reload();
        })
        .catch(error => handleException(error));

    });
  }
  function updateCartAmounts() {
    if (location.pathname != '/cart/') {
      return;  
    }
    $.ajax({
      type: 'GET',
      url: `${location.origin}/cart/amounts`,
      success: (html) => {
        document.querySelector(".cart-basement").outerHTML = html;
      },
      error: (error) => handleException(error)
    });
  }
  function handleCartItems(target) {
    const $addToCartBox = $(".addto-cart-box");
    if ($addToCartBox.length > 0 
        && $(target).parents('.product-quantity-box').length > 0) return;
    const $form = target.parent().find("form[name='cart-form']")[0];
    updateCart($form, target.data('url'))
      .then(cartItem => {
        updateCartCount(
          document.querySelector(`#cart-count-${cartItem.id}`),
          cartItem.quantity
        );
        updateCartCount(
          document.querySelector(".topbar__buttons .cart-count"),
          cartItem.total_quantity
        );
        const cartRow = target.parents("tr[name='cart-row']");
        if (cartRow)
          cartRow.find("td[name='total_price']")?.html(`р.${decimalFormat(cartItem.total_price, 1)}`);
        updateCartAmounts();
        updateCartQuantity(
          document.querySelector(`.product-quantity-box[name='product-quantity-box-${cartItem.id}'] form[name='cart-form'] input[name='quantity']`),
          cartItem.quantity
        );
      })
      .catch(error => handleException(error));  
  }
  function submitOrderEvent() {
    createOrder('confirmed')
      .then((response) => {
        if ('InvId' in response)
          location.href = $(this).data('url');
        $('.text-error').each((_, el) => {
          let key = el.attributes.name.nodeValue;
          if (key in response) {
            el.style.display = 'block';
            el.innerText = response[key];
          } else {
            el.style.display = 'none';
            el.innerText = '';
          }
        });
      })
      .catch((error) => console.log(error));
  }
  function createPaymentEvent() {
    createOrder('introductory')
    .then((response) => {
      if ('InvId' in response)
        createPayment(response.InvId);
      $('.text-error').each((_, el) => {
        let key = el.attributes.name.nodeValue;
        if (key in response) {
          el.style.display = 'block';
          el.innerText = response[key];
        } else {
          el.style.display = 'none';
          el.innerText = '';
        }
      });
    })
    .catch((error) => console.log(error));
  }
  function createPayment(InvId) {
    let $form = $('#payment-form');
    const formData = new FormData($form[0]);
    formData.append('InvId', InvId);
    $.ajax({
      url: '/enterprise/payments/params',
      type: 'POST',
      data: formData,
      contentType: false,
      processData: false,
      success: (params) => {
        sessionStorage.setItem('InvId', InvId);
        Robokassa.StartPayment(params);
        waitForDialog('#robokassa_iframe');
        
      },
      error: (error) => console.log(error)
    });
  }
  function createOrder(status='introductory') {
    let $form = $('#primary-form');
    let $additionalForm = $('#additional-form'); let additional_info = NaN;
    if ($additionalForm.find('input[name="address"]').val())
      $form = $additionalForm;
    else {
      additional_info = $("textarea[name='notes']").val()
    }
    const formData = new FormData($form[0]);
    if (additional_info) formData.append('additional_info', additional_info);
    formData.append('status', status);
    return $.ajax({
      type: 'POST',
      url: $form.attr('action'),
      data: formData,
      contentType: false,
      processData: false,
      success: (result) => {
        return result;
      },
      error: (error) => {
        throw error;
      }
    });
  }
  function cancelOrder(invId) {
    $.ajax({
      url: `/orders/remove/${invId}`,
      success: () => location.reload(),
      error: () => location.reload()
    });
  }
  function checkOrderPayment() {
    const invId = sessionStorage.getItem('InvId')
    const formData = new FormData();
    formData.append('InvId', invId);
    $.ajax({
      url: '/enterprise/payments/check',
      type: 'POST',
      data: formData,
      contentType: false,
      processData: false,
      success: (params) => {
        sessionStorage.removeItem('InvId');
        if(params.status == 0) {
          cancelOrder(invId);
        } else {
          location.href = `${location.origin}/catalog/products`;
        }            
      },
      error: () => cancelOrder(invId)
    });
  }
  function detectPaymentDialogClosed(observeElement) {
    const observedElement = document.querySelector(observeElement);
    const observer = new MutationObserver((mutationsList, observer) => {
      for (const mutation of mutationsList) {
        if (mutation.attributeName === 'style') {
          const visibility = window.getComputedStyle(observedElement).visibility;
          if (visibility === 'hidden') {
            checkOrderPayment();
          }
        }
      }
    });
    if(observedElement)
      observer.observe(
        observedElement, { attributes: true }
      );
    return () => observer.disconnect();
  }
  function handleException(error) {
    $(".error-popup").toggleClass("active");
    $('.mobile-nav__wrapper').removeClass('expanded');
    $("body").toggleClass("locked");

    $(".error-popup .error-toast .error-toast-body").text(`${error.status}: ${error.responseText}`);
  }

  // window load event
  $(window).on("load", function () {
    if ($(".preloader").length) {
      $(".preloader").fadeOut();
    }
    thmSwiperInit();
    thmTinyInit();

    if ($(".circle-progress").length) {
      $(".circle-progress").appear(function () {
        let circleProgress = $(".circle-progress");
        circleProgress.each(function () {
          let progress = $(this);
          let progressOptions = progress.data("options");
          progress.circleProgress(progressOptions);
        });
      });
    }

    if ($(".post-filter").length) {
      var postFilterList = $(".post-filter li");
      // for first init
      $(".filter-layout").isotope({
        filter: ".filter-item",
        animationOptions: {
          duration: 500,
          easing: "linear",
          queue: false
        }
      });
      // on click filter links
      postFilterList.on("click", function () {
        var Self = $(this);
        var selector = Self.attr("data-filter");
        postFilterList.removeClass("active");
        Self.addClass("active");

        $(".filter-layout").isotope({
          filter: selector,
          animationOptions: {
            duration: 500,
            easing: "linear",
            queue: false
          }
        });
        return false;
      });
    }

    if ($(".post-filter.has-dynamic-filter-counter").length) {
      // var allItem = $('.single-filter-item').length;

      var activeFilterItem = $(".post-filter.has-dynamic-filter-counter").find(
        "li"
      );

      activeFilterItem.each(function () {
        var filterElement = $(this).data("filter");
        var count = $(".filter-layout").find(filterElement).length;
        $(this).append("<sup>[" + count + "]</sup>");
      });
    }

    CartEvents();

  });

  // window scroll event
  $(window).on("scroll", function () {
    if ($(".stricked-menu").length) {
      var headerScrollPos = 130;
      var stricky = $(".stricked-menu");
      if ($(window).scrollTop() > headerScrollPos) {
        stricky.addClass("stricky-fixed");
      } else if ($(this).scrollTop() <= headerScrollPos) {
        stricky.removeClass("stricky-fixed");
      }
    }
    if ($(".scroll-to-top").length) {
      var strickyScrollPos = 100;
      if ($(window).scrollTop() > strickyScrollPos) {
        $(".scroll-to-top").fadeIn(500);
      } else if ($(this).scrollTop() <= strickyScrollPos) {
        $(".scroll-to-top").fadeOut(500);
      }
    }
  });

})(jQuery);
