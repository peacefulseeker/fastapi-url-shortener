class Form extends HTMLElement {
  constructor() {
    super();
    const origin = this.getAttribute("origin");
    const url = this.getAttribute("url");
    this.innerHTML = `
        <form class="flex flex-wrap items-center justify-center mx-auto pt-12 md:w-1/2"
                hx-post="${url}"
                hx-swap="none">

        <input type="url" name="full_url"
            autofocus
            required
            pattern="https?://.*"
            autocomplete="url"
            placeholder="Paste full URL"
            class="input input-bordered w-full mb-4" />

        <label class="input input-bordered flex items-center gap-2 pl-0 w-full mb-4">
            <span class="bg-neutral-100 flex items-center h-full px-2 rounded-l-md">${origin}</span>
            <input name="short_path" type="text" required autocomplete placeholder="shortpath" class="grow" maxlength="20" />
        </label>
        <button class="btn btn-primary w-full">Shorten</button>
    </form>
      `;
  }
}

customElements.define("c-form", Form);
