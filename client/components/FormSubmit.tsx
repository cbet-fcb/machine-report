import React from "react";

import ProgressLoading from "./ProgressLoading";

interface FormSubmitProps {
  data: {
    [key: string]: unknown;
  };
}

const FormSubmit: React.FC<FormSubmitProps> = ({ data }) => {
  // const [formData, setFormData] = React.useState<FormData | null>(null);s

  const [loading, setLoading] = React.useState(false);


  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    setLoading(true);

    fetch(
      "https://script.google.com/macros/s/AKfycbz7_7VGL8iAzRKhHTmx8zfBIEcoI_iQLevi-kpZwZvBxH_YkyvuXbpB9E5I4kMsROsqdw/exec",
      { method: "POST", body: formData }
    )
      .then((response) => alert("Thank you! Form is submitted"))
      .catch((error) => console.error("Error!", error.message))
      .finally(() => {
        setLoading(false);
        window.location.reload();
      });
  };
  return (
    <form
      onSubmit={handleSubmit}
      className="bg-base-100 flex justify-center rounded-box "
    >
      <ProgressLoading
        loading={loading}
        progressData={{ progress: 0, msg: "Submition on Progress" }}
      />
      <fieldset className=" fieldset rounded-box place-content-evenly border p-4 w-full">
        <legend className="fieldset-legend">Spreadsheet Submition</legend>

        {Object.entries(data).map(([key, value]) => (
          <div key={key} className="form-control w-full">
            <label className="label">
              <span className="label-text">{key}</span>
            </label>
            <input
              type="text"
              name={key}
              id={key}
              className="input input-bordered w-full"
              placeholder={key}
              defaultValue={JSON.stringify(value)}
            />
          </div>
        ))}

        {/* Uncomment the following lines to add email and password fields */}

        {/* <label className="label">Email</label>
        <input type="email" className="input" placeholder="Email" />

        <label className="label">Password</label>
        <input type="password" className="input" placeholder="Password" /> */}

        <button type="submit" className="btn btn-neutral mt-4">
          Submit
        </button>
      </fieldset>
    </form>
  );
};

export default FormSubmit;
