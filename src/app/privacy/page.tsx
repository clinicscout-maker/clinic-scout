import Link from "next/link";
import { ArrowLeft } from "lucide-react";

export default function PrivacyPage() {
    return (
        <div className="min-h-screen bg-slate-50 py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-3xl mx-auto">
                <div className="mb-8">
                    <Link
                        href="/"
                        className="inline-flex items-center text-sm font-medium text-slate-600 hover:text-blue-600 transition-colors"
                    >
                        <ArrowLeft className="w-4 h-4 mr-2" />
                        Back to Home
                    </Link>
                </div>

                <div className="bg-white rounded-2xl shadow-sm p-8 sm:p-12">
                    <h1 className="text-3xl font-bold text-slate-900 mb-8">Privacy Policy</h1>

                    <div className="space-y-8 text-slate-600">
                        <section>
                            <h2 className="text-xl font-semibold text-slate-900 mb-3">1. Data Collection</h2>
                            <p>
                                We collect the minimum amount of data necessary to provide our service:
                            </p>
                            <ul className="list-disc pl-5 mt-2 space-y-1">
                                <li><strong>Name:</strong> To personalize your experience.</li>
                                <li><strong>Email Address:</strong> Used for billing and account management.</li>
                                <li><strong>Phone Number:</strong> Strictly used for sending SMS availability alerts.</li>
                                <li><strong>Location Preferences:</strong> To filter alerts relevant to your area.</li>
                            </ul>
                        </section>

                        <section>
                            <h2 className="text-xl font-semibold text-slate-900 mb-3">2. Data Usage</h2>
                            <p>
                                Your data is used solely to operate the Clinic Scout service. We use your phone number to deliver real-time SMS notifications about clinic availability.
                                We use your email to verify your subscription status and communicate important service updates.
                            </p>
                        </section>

                        <section>
                            <h2 className="text-xl font-semibold text-slate-900 mb-3">3. Data Storage and Security</h2>
                            <p>
                                Your personal information is stored securely using Google Cloud Platform (Firebase).
                                We utilize industry-standard encryption and security practices. Data is stored in US/Canada regions to ensure reliability and compliance.
                            </p>
                        </section>

                        <section>
                            <h2 className="text-xl font-semibold text-slate-900 mb-3">4. Third-Party Sharing</h2>
                            <p>
                                We do not sell your personal data. We share data only with trusted third-party service providers necessary for our operations:
                            </p>
                            <ul className="list-disc pl-5 mt-2 space-y-1">
                                <li><strong>Ko-fi / PayPal:</strong> For processing secure payments. We do not store your credit card information.</li>
                                <li><strong>Twilio:</strong> For delivering SMS notifications to your phone.</li>
                            </ul>
                        </section>

                        <section>
                            <h2 className="text-xl font-semibold text-slate-900 mb-3">5. Your Rights</h2>
                            <p>
                                You have the right to access, correct, or delete your personal information at any time.
                                If you wish to delete your account and all associated data, please contact us or unsubscribe from the service.
                            </p>
                        </section>

                        <div className="pt-8 border-t border-slate-100 text-sm text-slate-500">
                            Last updated: November 2025
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
