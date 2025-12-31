export default function Profile() {
  return (
    <section
      className="min-h-screen bg-cover bg-center flex items-center justify-center"
      style={{
        backgroundImage: "url('/url_image.webp')",
      }}
    >
      <div className="bg-black/40 w-full h-full flex items-center justify-center">
        <h1 className="text-white text-5xl font-bold">
          Welcome to My Profile
        </h1>
      </div>
    </section>
  );
}
