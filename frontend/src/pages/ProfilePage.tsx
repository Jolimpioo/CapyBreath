import UserProfile from '../features/user/UserProfile';
import EditProfileForm from '../features/user/EditProfileForm';
import PageContainer from '../components/ui/PageContainer';

const ProfilePage = () => (
  <PageContainer className="max-w-6xl mt-2">
    <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_360px]">
      <UserProfile />
      <EditProfileForm />
    </div>
  </PageContainer>
);

export default ProfilePage;
